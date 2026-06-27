"""Studio experiment endpoint: run vector / graph / hybrid retrieval, compare,
and persist the run for benchmarking."""

import time
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import CurrentUser, DbSession, require_permission
from app.core import ratelimit
from app.core.config import settings
from app.core.permissions import RUN_EXPERIMENTS
from app.integrations import llm
from app.integrations.llm import LLMError, LLMNotConfigured
from app.models.user import User
from app.rag import generation, graph_retrieval, hybrid, retrieval
from app.schemas.studio import (
    EvaluationRunOut,
    ExperimentMetrics,
    ExperimentRequest,
    ExperimentResponse,
    StudioChunk,
    StudioTriple,
)
from app.services import audit_service, document_service, evaluation_service
from app.services import knowledge_base_service as kb_service

router = APIRouter(prefix="/studio", tags=["studio"])


def _usage_tokens(usage: dict) -> int | None:
    return usage.get("total_tokens") or usage.get("totalTokenCount")


@router.post("/experiments", response_model=ExperimentResponse)
async def run_experiment(
    payload: ExperimentRequest,
    db: DbSession,
    user: Annotated[User, Depends(require_permission(RUN_EXPERIMENTS))],
) -> ExperimentResponse:
    kb = await kb_service.get_for_org(db, payload.knowledge_base_id, user.organization_id)
    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found"
        )

    await ratelimit.enforce(user)
    start = time.monotonic()
    mode = payload.retrieval_mode
    chunks_for_gen: list = []
    vector_results: list[StudioChunk] = []
    triples: list[dict] = []

    # --- retrieval ---------------------------------------------------------
    if mode == "vector":
        retrieved = await retrieval.retrieve(kb, payload.query, payload.top_k)
        chunks_for_gen = retrieved
    elif mode == "hybrid":
        chunks_for_gen = await hybrid.hybrid_retrieve(
            kb, payload.query, payload.top_k, payload.fusion_strategy, payload.alpha
        )
    if mode in ("graph", "hybrid"):
        triples, _ = await graph_retrieval.retrieve(kb.id, payload.query)

    doc_ids = [uuid.UUID(c.document_id) for c in chunks_for_gen if c.document_id]
    names = await document_service.file_names_for(db, doc_ids)
    for c in chunks_for_gen:
        vector_results.append(
            StudioChunk(
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                file_name=names.get(c.document_id, "unknown"),
                chunk_index=c.chunk_index,
                text=c.text,
                score=getattr(c, "fused_score", None) or c.score,
                vector_score=getattr(c, "vector_score", None) or getattr(c, "score", None),
                lexical_score=getattr(c, "lexical_score", None),
                fused_score=getattr(c, "fused_score", None),
            )
        )

    # --- generation --------------------------------------------------------
    llm_configured = llm.is_configured()
    generation_error: str | None = None
    answer = ""
    usage: dict = {}
    if not chunks_for_gen and not triples:
        answer = "No relevant information found in this knowledge base."
    else:
        if mode == "graph":
            prompt, system = (
                generation.build_graph_prompt(payload.query, triples),
                generation.GRAPH_SYSTEM,
            )
        elif mode == "hybrid":
            prompt = generation.build_hybrid_prompt(payload.query, chunks_for_gen, triples)
            system = generation.SYSTEM_PROMPT
        else:
            prompt, system = (
                generation.build_prompt(payload.query, chunks_for_gen),
                generation.SYSTEM_PROMPT,
            )
        try:
            result = await llm.generate(prompt, system)
            answer, usage = result["text"], result["usage"]
        except LLMNotConfigured:
            llm_configured = False
        except LLMError as exc:
            generation_error = str(exc)

    latency_ms = int((time.monotonic() - start) * 1000)
    vector_scores = [c.vector_score for c in vector_results if c.vector_score is not None]
    score = round(sum(vector_scores) / len(vector_scores), 4) if vector_scores else None
    token_usage = _usage_tokens(usage)

    run = await evaluation_service.create_run(
        db,
        user_id=user.id,
        workspace_id=kb.workspace_id,
        knowledge_base_id=kb.id,
        retrieval_mode=mode,
        embedding_model=kb.embedding_model,
        reranker=payload.fusion_strategy if mode == "hybrid" else None,
        chunk_size=settings.chunk_size,
        top_k=payload.top_k,
        latency_ms=latency_ms,
        token_usage=token_usage,
        cost=None,
        score=score,
        hallucination_score=None,
    )
    await audit_service.log(
        db,
        organization_id=user.organization_id,
        actor_id=user.id,
        action="experiment.run",
        resource_type="knowledge_base",
        resource_id=str(kb.id),
        metadata={"mode": mode, "top_k": payload.top_k},
    )

    return ExperimentResponse(
        run_id=run.id,
        retrieval_mode=mode,
        answer=answer,
        vector_results=vector_results,
        graph_results=[StudioTriple(**t) for t in triples],
        metrics=ExperimentMetrics(
            latency_ms=latency_ms,
            token_usage=token_usage,
            score=score,
            retrieved_count=len(vector_results),
            relationship_count=len(triples),
        ),
        model=llm.active_model(),
        llm_configured=llm_configured,
        generation_error=generation_error,
    )


@router.get("/experiments", response_model=list[EvaluationRunOut])
async def list_experiments(
    user: CurrentUser,
    db: DbSession,
    workspace_id: Annotated[uuid.UUID, Query()],
) -> list[EvaluationRunOut]:
    # Scope: workspace must belong to the user's org.
    if not await kb_service.workspace_in_org(db, workspace_id, user.organization_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return await evaluation_service.list_for_workspace(db, workspace_id)

"""Graph RAG endpoints: graph inspection + relationship-aware querying."""

import time
import uuid

from fastapi import APIRouter, HTTPException, status
from starlette.concurrency import run_in_threadpool

from app.api.deps import CurrentUser, DbSession
from app.integrations import llm
from app.integrations.llm import LLMError, LLMNotConfigured
from app.rag import generation, graph_retrieval, graph_store
from app.schemas.graph import (
    EntityOut,
    GraphQueryRequest,
    GraphQueryResponse,
    GraphStats,
    GraphTriple,
)
from app.services import knowledge_base_service as kb_service

router = APIRouter(prefix="/knowledge-bases", tags=["graph"])


async def _require_kb(db, kb_id: uuid.UUID, org_id: uuid.UUID):
    kb = await kb_service.get_for_org(db, kb_id, org_id)
    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found"
        )
    return kb


@router.get("/{kb_id}/graph/entities", response_model=list[EntityOut])
async def list_entities(kb_id: uuid.UUID, user: CurrentUser, db: DbSession) -> list[EntityOut]:
    await _require_kb(db, kb_id, user.organization_id)
    rows = await run_in_threadpool(graph_store.get_entities, str(kb_id))
    return [EntityOut(**r) for r in rows]


@router.get("/{kb_id}/graph/relationships", response_model=list[GraphTriple])
async def list_relationships(
    kb_id: uuid.UUID, user: CurrentUser, db: DbSession
) -> list[GraphTriple]:
    await _require_kb(db, kb_id, user.organization_id)
    rows = await run_in_threadpool(graph_store.get_relationships, str(kb_id))
    return [GraphTriple(**r) for r in rows]


@router.get("/{kb_id}/graph/stats", response_model=GraphStats)
async def graph_stats(kb_id: uuid.UUID, user: CurrentUser, db: DbSession) -> GraphStats:
    await _require_kb(db, kb_id, user.organization_id)
    return GraphStats(**await run_in_threadpool(graph_store.stats, str(kb_id)))


@router.post("/{kb_id}/graph-query", response_model=GraphQueryResponse)
async def graph_query(
    kb_id: uuid.UUID, payload: GraphQueryRequest, user: CurrentUser, db: DbSession
) -> GraphQueryResponse:
    await _require_kb(db, kb_id, user.organization_id)
    start = time.monotonic()
    triples, seeds = await graph_retrieval.retrieve(kb_id, payload.query)

    llm_configured = llm.is_configured()
    generation_error: str | None = None
    if not triples:
        answer = "I couldn't find related entities in the knowledge graph for this question."
    else:
        answer = ""
        try:
            answer = (
                await llm.generate(
                    generation.build_graph_prompt(payload.query, triples), generation.GRAPH_SYSTEM
                )
            )["text"]
        except LLMNotConfigured:
            llm_configured = False
        except LLMError as exc:
            generation_error = str(exc)

    return GraphQueryResponse(
        answer=answer,
        relationships=[GraphTriple(**t) for t in triples],
        seed_entities=seeds,
        model=llm.active_model(),
        llm_configured=llm_configured,
        generation_error=generation_error,
        latency_ms=int((time.monotonic() - start) * 1000),
    )

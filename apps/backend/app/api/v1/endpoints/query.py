"""Vector RAG query endpoint: retrieve relevant chunks + generate a grounded answer."""

import time
import uuid

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.integrations import llm
from app.integrations.llm import LLMError, LLMNotConfigured
from app.rag import generation, retrieval
from app.schemas.query import CitationOut, QueryRequest, QueryResponse, RetrievedChunkOut
from app.services import document_service
from app.services import knowledge_base_service as kb_service

router = APIRouter(prefix="/knowledge-bases", tags=["query"])


@router.post("/{kb_id}/query", response_model=QueryResponse)
async def query_knowledge_base(
    kb_id: uuid.UUID, payload: QueryRequest, user: CurrentUser, db: DbSession
) -> QueryResponse:
    kb = await kb_service.get_for_org(db, kb_id, user.organization_id)
    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found"
        )

    start = time.monotonic()
    chunks = await retrieval.retrieve(kb, payload.query, payload.top_k)

    names = await document_service.file_names_for(
        db, [uuid.UUID(d) for d in {c.document_id for c in chunks} if d]
    )

    llm_configured = llm.is_configured()
    generation_error: str | None = None
    answer = ""
    try:
        answer = (await generation.generate_answer(payload.query, chunks))["text"]
    except LLMNotConfigured:
        llm_configured = False
    except LLMError as exc:
        # Retrieval still succeeded — return chunks and surface the LLM failure.
        generation_error = str(exc)

    return QueryResponse(
        answer=answer,
        citations=[
            CitationOut(
                index=i + 1,
                document_id=c.document_id,
                file_name=names.get(c.document_id, "unknown"),
                score=c.score,
            )
            for i, c in enumerate(chunks)
        ],
        retrieved=[
            RetrievedChunkOut(
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                chunk_index=c.chunk_index,
                score=c.score,
                text=c.text,
            )
            for c in chunks
        ],
        model=llm.active_model(),
        llm_configured=llm_configured,
        generation_error=generation_error,
        latency_ms=int((time.monotonic() - start) * 1000),
    )

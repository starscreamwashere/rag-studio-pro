"""Vector retrieval: embed query -> Qdrant top-k search."""

import uuid
from dataclasses import dataclass

from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.models.knowledge_base import KnowledgeBase
from app.rag import embeddings, vector_store


@dataclass
class RetrievedChunk:
    chunk_id: str
    document_id: str
    chunk_index: int
    text: str
    score: float


async def retrieve(
    kb: KnowledgeBase, query: str, top_k: int | None = None, document_id: str | None = None
) -> list[RetrievedChunk]:
    top_k = top_k or settings.retrieval_top_k
    query_vector = await run_in_threadpool(embeddings.embed_query, kb.embedding_model, query)
    name = vector_store.collection_name(
        kb.id if isinstance(kb.id, uuid.UUID) else uuid.UUID(str(kb.id))
    )
    hits = await run_in_threadpool(vector_store.search, name, query_vector, top_k, document_id)
    return [
        RetrievedChunk(
            chunk_id=str(h.payload.get("chunk_id", h.id)),
            document_id=str(h.payload.get("document_id", "")),
            chunk_index=int(h.payload.get("chunk_index", 0)),
            text=h.payload.get("text", ""),
            score=float(h.score),
        )
        for h in hits
    ]

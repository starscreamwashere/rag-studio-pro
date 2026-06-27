"""Hybrid retrieval: fuse dense (vector) and sparse (lexical) rankings.

Vector candidates are pulled from Qdrant, re-scored lexically (query-term
coverage), and the two rankings are fused via weighted sum or reciprocal-rank
fusion (RRF). Graph context is added separately by the Studio.
"""

import re
import uuid
from dataclasses import dataclass

from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.models.knowledge_base import KnowledgeBase
from app.rag import embeddings, vector_store

_WORD_RE = re.compile(r"[a-z0-9]+")
_RRF_K = 60


@dataclass
class HybridChunk:
    chunk_id: str
    document_id: str
    chunk_index: int
    text: str
    vector_score: float
    lexical_score: float
    fused_score: float


def _lexical_score(query: str, text: str) -> float:
    """Fraction of distinct query terms present in the chunk (sparse signal)."""
    q = set(_WORD_RE.findall(query.lower()))
    if not q:
        return 0.0
    present = sum(1 for term in q if term in text.lower())
    return present / len(q)


def _minmax(values: list[float]) -> list[float]:
    lo, hi = min(values), max(values)
    if hi - lo < 1e-9:
        return [1.0 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


async def hybrid_retrieve(
    kb: KnowledgeBase,
    query: str,
    top_k: int | None = None,
    fusion_strategy: str = "rrf",
    alpha: float = 0.5,
) -> list[HybridChunk]:
    top_k = top_k or settings.retrieval_top_k
    candidate_n = max(top_k * 3, 12)

    query_vector = await run_in_threadpool(embeddings.embed_query, kb.embedding_model, query)
    name = vector_store.collection_name(
        kb.id if isinstance(kb.id, uuid.UUID) else uuid.UUID(str(kb.id))
    )
    hits = await run_in_threadpool(vector_store.search, name, query_vector, candidate_n, None)
    if not hits:
        return []

    candidates = [
        {
            "chunk_id": str(h.payload.get("chunk_id", h.id)),
            "document_id": str(h.payload.get("document_id", "")),
            "chunk_index": int(h.payload.get("chunk_index", 0)),
            "text": h.payload.get("text", ""),
            "vector_score": float(h.score),
            "lexical_score": _lexical_score(query, h.payload.get("text", "")),
        }
        for h in hits
    ]

    # Ranks (1 = best) for RRF.
    by_vec = sorted(
        range(len(candidates)), key=lambda i: candidates[i]["vector_score"], reverse=True
    )
    by_lex = sorted(
        range(len(candidates)), key=lambda i: candidates[i]["lexical_score"], reverse=True
    )
    vec_rank = {idx: r + 1 for r, idx in enumerate(by_vec)}
    lex_rank = {idx: r + 1 for r, idx in enumerate(by_lex)}

    if fusion_strategy == "weighted":
        nv = _minmax([c["vector_score"] for c in candidates])
        nl = _minmax([c["lexical_score"] for c in candidates])
        fused = [alpha * nv[i] + (1 - alpha) * nl[i] for i in range(len(candidates))]
    else:  # reciprocal rank fusion
        fused = [
            1 / (_RRF_K + vec_rank[i]) + 1 / (_RRF_K + lex_rank[i]) for i in range(len(candidates))
        ]

    results = [
        HybridChunk(
            chunk_id=c["chunk_id"],
            document_id=c["document_id"],
            chunk_index=c["chunk_index"],
            text=c["text"],
            vector_score=round(c["vector_score"], 4),
            lexical_score=round(c["lexical_score"], 4),
            fused_score=round(fused[i], 6),
        )
        for i, c in enumerate(candidates)
    ]
    results.sort(key=lambda r: r.fused_score, reverse=True)
    return results[:top_k]

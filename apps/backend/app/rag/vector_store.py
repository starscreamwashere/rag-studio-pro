"""Qdrant vector store — one collection per knowledge base.

Synchronous client; async callers wrap calls in a threadpool.
"""

import uuid
from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.core.config import settings


@lru_cache(maxsize=1)
def get_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)


def collection_name(kb_id: uuid.UUID) -> str:
    return f"kb_{kb_id.hex}"


def ensure_collection(name: str, dim: int) -> None:
    client = get_client()
    if not client.collection_exists(name):
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )


def upsert_points(name: str, points: list[dict]) -> None:
    get_client().upsert(
        collection_name=name,
        points=[PointStruct(id=p["id"], vector=p["vector"], payload=p["payload"]) for p in points],
    )


def search(name: str, query_vector: list[float], top_k: int, document_id: str | None = None):
    client = get_client()
    if not client.collection_exists(name):
        return []
    query_filter = None
    if document_id:
        query_filter = Filter(
            must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
        )
    return client.query_points(
        collection_name=name,
        query=query_vector,
        limit=top_k,
        query_filter=query_filter,
        with_payload=True,
    ).points


def delete_collection(name: str) -> None:
    client = get_client()
    if client.collection_exists(name):
        client.delete_collection(name)

"""Studio experiment schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ExperimentRequest(BaseModel):
    knowledge_base_id: uuid.UUID
    query: str = Field(min_length=1, max_length=4000)
    retrieval_mode: str = Field(default="hybrid", pattern="^(vector|graph|hybrid)$")
    top_k: int = Field(default=5, ge=1, le=20)
    fusion_strategy: str = Field(default="rrf", pattern="^(rrf|weighted)$")
    alpha: float = Field(default=0.5, ge=0.0, le=1.0)


class StudioChunk(BaseModel):
    chunk_id: str
    document_id: str
    file_name: str
    chunk_index: int
    text: str
    score: float
    vector_score: float | None = None
    lexical_score: float | None = None
    fused_score: float | None = None


class StudioTriple(BaseModel):
    source: str
    relation: str
    target: str


class ExperimentMetrics(BaseModel):
    latency_ms: int
    token_usage: int | None
    score: float | None
    retrieved_count: int
    relationship_count: int


class ExperimentResponse(BaseModel):
    run_id: uuid.UUID
    retrieval_mode: str
    answer: str
    vector_results: list[StudioChunk]
    graph_results: list[StudioTriple]
    metrics: ExperimentMetrics
    model: str
    llm_configured: bool
    generation_error: str | None = None


class EvaluationRunOut(ORMModel):
    id: uuid.UUID
    knowledge_base_id: uuid.UUID | None
    retrieval_mode: str
    embedding_model: str
    reranker: str | None
    chunk_size: int | None
    top_k: int
    latency_ms: int
    token_usage: int | None
    score: float | None
    created_at: datetime

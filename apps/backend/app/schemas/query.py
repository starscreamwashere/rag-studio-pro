"""Vector RAG query schemas."""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    top_k: int | None = Field(default=None, ge=1, le=20)


class RetrievedChunkOut(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    score: float
    text: str


class CitationOut(BaseModel):
    index: int
    document_id: str
    file_name: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    citations: list[CitationOut]
    retrieved: list[RetrievedChunkOut]
    model: str
    llm_configured: bool
    generation_error: str | None = None
    latency_ms: int

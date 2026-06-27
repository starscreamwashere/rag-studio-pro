"""Graph RAG schemas."""

from pydantic import BaseModel, Field


class GraphTriple(BaseModel):
    source: str
    relation: str
    target: str


class EntityOut(BaseModel):
    id: str | None
    name: str
    type: str | None
    degree: int


class GraphStats(BaseModel):
    entities: int
    relationships: int


class GraphQueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)


class GraphQueryResponse(BaseModel):
    answer: str
    relationships: list[GraphTriple]
    seed_entities: list[str]
    model: str
    llm_configured: bool
    generation_error: str | None = None
    latency_ms: int

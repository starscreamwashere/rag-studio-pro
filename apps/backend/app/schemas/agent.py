"""Agent (Phase 7) request/response schemas."""

import uuid

from pydantic import BaseModel, Field


class AgentMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=8000)
    allow_web_search: bool = False


class AgentSource(BaseModel):
    index: int
    document_id: str
    file_name: str
    score: float
    snippet: str


class AgentResponse(BaseModel):
    message_id: uuid.UUID
    answer: str
    trace: list[dict]
    sources: list[AgentSource]
    confidence: float | None = None
    needs_approval: bool = False
    model: str
    llm_configured: bool
    generation_error: str | None = None

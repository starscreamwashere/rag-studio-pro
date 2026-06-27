"""Chat session / message schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ChatSessionCreate(BaseModel):
    knowledge_base_id: uuid.UUID
    title: str | None = Field(default=None, max_length=255)


class ChatSessionRead(ORMModel):
    id: uuid.UUID
    knowledge_base_id: uuid.UUID | None
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class MessageRead(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    citations: list | None = None
    confidence_score: float | None = None
    created_at: datetime


class ChatSessionDetail(ChatSessionRead):
    messages: list[MessageRead] = []


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=8000)

"""Knowledge base, document, and ingestion-job schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class KnowledgeBaseCreate(BaseModel):
    workspace_id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class KnowledgeBaseRead(ORMModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    description: str | None
    embedding_model: str
    retrieval_default: str
    status: str
    created_at: datetime
    document_count: int = 0


class DocumentRead(ORMModel):
    id: uuid.UUID
    knowledge_base_id: uuid.UUID
    file_name: str
    file_type: str
    file_size: int
    ingestion_status: str
    uploaded_at: datetime


class IngestionJobRead(ORMModel):
    id: uuid.UUID
    document_id: uuid.UUID
    status: str
    current_step: str | None
    progress_percent: int
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None

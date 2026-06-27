"""Admin module schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel


class AuditLogOut(ORMModel):
    id: uuid.UUID
    actor_id: uuid.UUID | None
    action: str
    resource_type: str
    resource_id: str | None
    metadata_json: dict | None
    timestamp: datetime


class UsageSummary(BaseModel):
    knowledge_bases: int
    documents: int
    experiments: int
    audit_events: int

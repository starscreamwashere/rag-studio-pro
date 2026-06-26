"""Organization & workspace schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class OrganizationCreate(BaseModel):
    """Onboarding payload: creates the org plus its first workspace."""

    name: str = Field(min_length=1, max_length=255)
    workspace_name: str = Field(default="Default Workspace", min_length=1, max_length=255)


class OrganizationRead(ORMModel):
    id: uuid.UUID
    name: str
    slug: str
    plan: str
    created_at: datetime


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class WorkspaceRead(ORMModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime

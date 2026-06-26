"""Auth / user-facing schemas."""

import uuid
from datetime import datetime

from app.schemas.common import ORMModel


class RoleRead(ORMModel):
    id: uuid.UUID
    name: str
    permissions: list[str]


class UserRead(ORMModel):
    id: uuid.UUID
    clerk_user_id: str
    organization_id: uuid.UUID
    email: str
    full_name: str | None
    role: RoleRead
    created_at: datetime

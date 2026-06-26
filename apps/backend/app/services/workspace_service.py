"""Workspace operations."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace import Workspace


async def list_workspaces(db: AsyncSession, organization_id: uuid.UUID) -> list[Workspace]:
    result = await db.execute(
        select(Workspace)
        .where(Workspace.organization_id == organization_id)
        .order_by(Workspace.created_at)
    )
    return list(result.scalars().all())


async def create_workspace(
    db: AsyncSession,
    organization_id: uuid.UUID,
    name: str,
    description: str | None = None,
) -> Workspace:
    workspace = Workspace(
        organization_id=organization_id,
        name=name,
        description=description,
    )
    db.add(workspace)
    await db.commit()
    await db.refresh(workspace)
    return workspace

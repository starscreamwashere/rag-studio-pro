"""Knowledge base operations (organization-scoped)."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.knowledge_base import KnowledgeBase
from app.models.workspace import Workspace


async def list_for_org(
    db: AsyncSession, organization_id: uuid.UUID, workspace_id: uuid.UUID | None = None
) -> list[KnowledgeBase]:
    stmt = (
        select(KnowledgeBase)
        .join(Workspace, KnowledgeBase.workspace_id == Workspace.id)
        .where(Workspace.organization_id == organization_id)
        .order_by(KnowledgeBase.created_at.desc())
    )
    if workspace_id is not None:
        stmt = stmt.where(KnowledgeBase.workspace_id == workspace_id)
    return list((await db.execute(stmt)).scalars().all())


async def document_counts(db: AsyncSession, kb_ids: list[uuid.UUID]) -> dict[uuid.UUID, int]:
    if not kb_ids:
        return {}
    stmt = (
        select(Document.knowledge_base_id, func.count())
        .where(Document.knowledge_base_id.in_(kb_ids))
        .group_by(Document.knowledge_base_id)
    )
    return {row[0]: row[1] for row in (await db.execute(stmt)).all()}


async def get_for_org(
    db: AsyncSession, kb_id: uuid.UUID, organization_id: uuid.UUID
) -> KnowledgeBase | None:
    stmt = (
        select(KnowledgeBase)
        .join(Workspace, KnowledgeBase.workspace_id == Workspace.id)
        .where(KnowledgeBase.id == kb_id, Workspace.organization_id == organization_id)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def workspace_in_org(
    db: AsyncSession, workspace_id: uuid.UUID, organization_id: uuid.UUID
) -> bool:
    ws = await db.get(Workspace, workspace_id)
    return ws is not None and ws.organization_id == organization_id


async def create(
    db: AsyncSession,
    workspace_id: uuid.UUID,
    name: str,
    description: str | None,
    created_by: uuid.UUID,
    embedding_model: str = "minilm",
    chunking_strategy: str = "recursive",
) -> KnowledgeBase:
    kb = KnowledgeBase(
        workspace_id=workspace_id,
        name=name,
        description=description,
        created_by=created_by,
        embedding_model=embedding_model,
        chunking_strategy=chunking_strategy,
    )
    db.add(kb)
    await db.commit()
    await db.refresh(kb)
    return kb


async def delete(db: AsyncSession, kb: KnowledgeBase) -> None:
    await db.delete(kb)
    await db.commit()

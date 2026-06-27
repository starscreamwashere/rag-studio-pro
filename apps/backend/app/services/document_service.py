"""Document + ingestion-job operations."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.ingestion_job import IngestionJob
from app.models.knowledge_base import KnowledgeBase
from app.models.workspace import Workspace


async def list_for_kb(db: AsyncSession, kb_id: uuid.UUID) -> list[Document]:
    stmt = (
        select(Document)
        .where(Document.knowledge_base_id == kb_id)
        .order_by(Document.uploaded_at.desc())
    )
    return list((await db.execute(stmt)).scalars().all())


async def create_with_job(
    db: AsyncSession,
    *,
    document_id: uuid.UUID,
    kb_id: uuid.UUID,
    file_name: str,
    file_type: str,
    file_size: int,
    storage_url: str,
    uploaded_by: uuid.UUID,
) -> tuple[Document, IngestionJob]:
    """Register the uploaded document and its queued ingestion job atomically."""
    doc = Document(
        id=document_id,
        knowledge_base_id=kb_id,
        file_name=file_name,
        file_type=file_type,
        file_size=file_size,
        storage_url=storage_url,
        ingestion_status="pending",
        uploaded_by=uploaded_by,
    )
    db.add(doc)
    await db.flush()
    job = IngestionJob(document_id=doc.id, status="queued")
    db.add(job)
    await db.commit()
    await db.refresh(doc)
    await db.refresh(job)
    return doc, job


async def get_for_org(
    db: AsyncSession, document_id: uuid.UUID, organization_id: uuid.UUID
) -> Document | None:
    stmt = (
        select(Document)
        .join(KnowledgeBase, Document.knowledge_base_id == KnowledgeBase.id)
        .join(Workspace, KnowledgeBase.workspace_id == Workspace.id)
        .where(Document.id == document_id, Workspace.organization_id == organization_id)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def latest_job(db: AsyncSession, document_id: uuid.UUID) -> IngestionJob | None:
    stmt = (
        select(IngestionJob)
        .where(IngestionJob.document_id == document_id)
        .order_by(IngestionJob.created_at.desc())
        .limit(1)
    )
    return (await db.execute(stmt)).scalar_one_or_none()

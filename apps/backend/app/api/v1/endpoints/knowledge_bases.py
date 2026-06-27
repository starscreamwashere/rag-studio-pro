"""Knowledge base endpoints (organization-scoped, RBAC-gated)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from starlette.concurrency import run_in_threadpool

from app.api.deps import CurrentUser, DbSession, require_permission
from app.core.config import settings
from app.core.permissions import CREATE_KNOWLEDGE_BASE
from app.integrations import storage
from app.models.knowledge_base import KnowledgeBase
from app.models.user import User
from app.rag import graph_store, vector_store
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseRead
from app.services import knowledge_base_service as kb_service

router = APIRouter(prefix="/knowledge-bases", tags=["knowledge-bases"])


def _to_read(kb: KnowledgeBase, count: int) -> KnowledgeBaseRead:
    read = KnowledgeBaseRead.model_validate(kb)
    read.document_count = count
    return read


@router.get("", response_model=list[KnowledgeBaseRead])
async def list_knowledge_bases(
    user: CurrentUser,
    db: DbSession,
    workspace_id: Annotated[uuid.UUID | None, Query()] = None,
) -> list[KnowledgeBaseRead]:
    kbs = await kb_service.list_for_org(db, user.organization_id, workspace_id)
    counts = await kb_service.document_counts(db, [kb.id for kb in kbs])
    return [_to_read(kb, counts.get(kb.id, 0)) for kb in kbs]


@router.post("", response_model=KnowledgeBaseRead, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    payload: KnowledgeBaseCreate,
    db: DbSession,
    user: Annotated[User, Depends(require_permission(CREATE_KNOWLEDGE_BASE))],
) -> KnowledgeBaseRead:
    if not await kb_service.workspace_in_org(db, payload.workspace_id, user.organization_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    kb = await kb_service.create(
        db,
        payload.workspace_id,
        payload.name,
        payload.description,
        user.id,
        payload.embedding_model,
        payload.chunking_strategy,
    )
    return _to_read(kb, 0)


@router.get("/{kb_id}", response_model=KnowledgeBaseRead)
async def get_knowledge_base(
    kb_id: uuid.UUID, user: CurrentUser, db: DbSession
) -> KnowledgeBaseRead:
    kb = await kb_service.get_for_org(db, kb_id, user.organization_id)
    if kb is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    counts = await kb_service.document_counts(db, [kb.id])
    return _to_read(kb, counts.get(kb.id, 0))


@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base(
    kb_id: uuid.UUID,
    db: DbSession,
    user: Annotated[User, Depends(require_permission(CREATE_KNOWLEDGE_BASE))],
) -> None:
    kb = await kb_service.get_for_org(db, kb_id, user.organization_id)
    if kb is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    # Remove stored objects + the vector collection before dropping the metadata
    # (which cascades documents/jobs/chunks).
    await run_in_threadpool(storage.delete_prefix, settings.minio_documents_bucket, f"{kb_id}/")
    await run_in_threadpool(vector_store.delete_collection, vector_store.collection_name(kb_id))
    await run_in_threadpool(graph_store.delete_kb_graph, str(kb_id))
    await kb_service.delete(db, kb)

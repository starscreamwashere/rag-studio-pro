"""Document upload + ingestion-status endpoints."""

import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from starlette.concurrency import run_in_threadpool

from app.api.deps import CurrentUser, DbSession, require_permission
from app.core.config import settings
from app.core.permissions import UPLOAD_DOCUMENTS
from app.ingestion.parsers import SUPPORTED_TYPES, normalize_type
from app.integrations import storage
from app.models.user import User
from app.schemas.knowledge_base import DocumentRead, IngestionJobRead
from app.services import audit_service, document_service
from app.services import knowledge_base_service as kb_service
from app.worker.tasks.ingestion import ingest_document

router = APIRouter(tags=["documents"])


@router.get("/knowledge-bases/{kb_id}/documents", response_model=list[DocumentRead])
async def list_documents(kb_id: uuid.UUID, user: CurrentUser, db: DbSession) -> list[DocumentRead]:
    if await kb_service.get_for_org(db, kb_id, user.organization_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found"
        )
    return await document_service.list_for_kb(db, kb_id)


@router.post(
    "/knowledge-bases/{kb_id}/documents",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    kb_id: uuid.UUID,
    db: DbSession,
    user: Annotated[User, Depends(require_permission(UPLOAD_DOCUMENTS))],
    file: Annotated[UploadFile, File()],
) -> DocumentRead:
    if await kb_service.get_for_org(db, kb_id, user.organization_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found"
        )

    file_name = Path(file.filename or "upload").name
    ext = normalize_type(Path(file_name).suffix)
    if ext not in SUPPORTED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '.{ext}'. Allowed: {', '.join(sorted(SUPPORTED_TYPES))}",
        )

    data = await file.read()
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.max_upload_mb} MB limit",
        )

    document_id = uuid.uuid4()
    key = f"{kb_id}/{document_id}/{file_name}"
    await run_in_threadpool(
        storage.upload_bytes,
        settings.minio_documents_bucket,
        key,
        data,
        file.content_type or "application/octet-stream",
    )

    doc, job = await document_service.create_with_job(
        db,
        document_id=document_id,
        kb_id=kb_id,
        file_name=file_name,
        file_type=ext,
        file_size=len(data),
        storage_url=key,
        uploaded_by=user.id,
    )
    # Hand off to the Celery worker for parsing.
    ingest_document.delay(str(doc.id), str(job.id))
    await audit_service.log(
        db,
        organization_id=user.organization_id,
        actor_id=user.id,
        action="document.uploaded",
        resource_type="document",
        resource_id=str(doc.id),
        metadata={"file_name": doc.file_name, "knowledge_base_id": str(kb_id)},
    )
    return doc


@router.get("/documents/{document_id}", response_model=DocumentRead)
async def get_document(document_id: uuid.UUID, user: CurrentUser, db: DbSession) -> DocumentRead:
    doc = await document_service.get_for_org(db, document_id, user.organization_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return doc


@router.get("/documents/{document_id}/job", response_model=IngestionJobRead)
async def get_document_job(
    document_id: uuid.UUID, user: CurrentUser, db: DbSession
) -> IngestionJobRead:
    if await document_service.get_for_org(db, document_id, user.organization_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    job = await document_service.latest_job(db, document_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No job for document")
    return job

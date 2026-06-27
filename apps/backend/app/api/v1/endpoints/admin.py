"""Admin module (role-restricted): audit monitoring + usage."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select

from app.api.deps import DbSession, require_permission
from app.core.permissions import MANAGE_USERS
from app.models.audit_log import AuditLog
from app.models.document import Document
from app.models.evaluation_run import EvaluationRun
from app.models.knowledge_base import KnowledgeBase
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.admin import AuditLogOut, UsageSummary
from app.services import audit_service

router = APIRouter(prefix="/admin", tags=["admin"])

AdminUser = Annotated[User, Depends(require_permission(MANAGE_USERS))]


@router.get("/audit-logs", response_model=list[AuditLogOut])
async def audit_logs(user: AdminUser, db: DbSession) -> list[AuditLogOut]:
    return await audit_service.list_for_org(db, user.organization_id)


@router.get("/usage", response_model=UsageSummary)
async def usage(user: AdminUser, db: DbSession) -> UsageSummary:
    org = user.organization_id

    kb_count = await db.scalar(
        select(func.count())
        .select_from(KnowledgeBase)
        .join(Workspace, KnowledgeBase.workspace_id == Workspace.id)
        .where(Workspace.organization_id == org)
    )
    doc_count = await db.scalar(
        select(func.count())
        .select_from(Document)
        .join(KnowledgeBase, Document.knowledge_base_id == KnowledgeBase.id)
        .join(Workspace, KnowledgeBase.workspace_id == Workspace.id)
        .where(Workspace.organization_id == org)
    )
    exp_count = await db.scalar(
        select(func.count())
        .select_from(EvaluationRun)
        .join(Workspace, EvaluationRun.workspace_id == Workspace.id)
        .where(Workspace.organization_id == org)
    )
    audit_count = await db.scalar(
        select(func.count()).select_from(AuditLog).where(AuditLog.organization_id == org)
    )
    return UsageSummary(
        knowledge_bases=kb_count or 0,
        documents=doc_count or 0,
        experiments=exp_count or 0,
        audit_events=audit_count or 0,
    )

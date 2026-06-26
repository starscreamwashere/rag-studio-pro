"""Workspace endpoints (scoped to the current user's organization)."""

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.organization import WorkspaceCreate, WorkspaceRead
from app.services import workspace_service

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceRead])
async def list_workspaces(user: CurrentUser, db: DbSession) -> list[WorkspaceRead]:
    return await workspace_service.list_workspaces(db, user.organization_id)


@router.post("", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreate,
    user: CurrentUser,
    db: DbSession,
) -> WorkspaceRead:
    return await workspace_service.create_workspace(
        db, user.organization_id, payload.name, payload.description
    )

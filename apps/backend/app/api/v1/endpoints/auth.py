"""Authenticated user endpoints."""

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.auth import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserRead)
async def me(user: CurrentUser) -> UserRead:
    """Return the current user. 404 ``onboarding_required`` if not yet onboarded."""
    return user

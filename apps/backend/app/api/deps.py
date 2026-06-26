"""Shared API dependencies: authentication and authorization."""

from collections.abc import Callable, Coroutine
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import AuthError, verify_clerk_token
from app.db.session import get_db
from app.models.user import User
from app.services.user_service import get_user_by_clerk_id

_bearer = HTTPBearer(auto_error=True)

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_clerk_claims(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
) -> dict:
    """Verify the Bearer token and return its claims."""
    try:
        return verify_clerk_token(credentials.credentials)
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


ClerkClaims = Annotated[dict, Depends(get_clerk_claims)]


async def get_current_user(claims: ClerkClaims, db: DbSession) -> User:
    """Load the authenticated user, or signal that onboarding is required."""
    user = await get_user_by_clerk_id(db, claims["sub"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="onboarding_required",
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_permission(
    permission: str,
) -> Callable[[User], Coroutine[Any, Any, User]]:
    """Dependency factory enforcing an RBAC permission on the current user."""

    async def checker(user: CurrentUser) -> User:
        if permission not in user.role.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission}",
            )
        return user

    return checker

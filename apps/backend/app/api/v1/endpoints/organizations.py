"""Organization endpoints, including onboarding."""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import ClerkClaims, CurrentUser, DbSession
from app.integrations.clerk import fetch_clerk_user
from app.schemas.organization import OrganizationCreate, OrganizationRead
from app.services import organization_service
from app.services.organization_service import OnboardingError
from app.services.user_service import get_user_by_clerk_id

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
async def create_organization(
    payload: OrganizationCreate,
    claims: ClerkClaims,
    db: DbSession,
) -> OrganizationRead:
    """Onboard the authenticated Clerk user: create org + first workspace + owner."""
    existing = await get_user_by_clerk_id(db, claims["sub"])
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already belongs to an organization.",
        )

    clerk_user = await fetch_clerk_user(claims["sub"])
    try:
        organization, _ = await organization_service.create_organization_with_owner(
            db, clerk_user, payload.name, payload.workspace_name
        )
    except OnboardingError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    return organization


@router.get("/current", response_model=OrganizationRead)
async def current_organization(user: CurrentUser, db: DbSession) -> OrganizationRead:
    organization = await organization_service.get_organization(db, user.organization_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return organization

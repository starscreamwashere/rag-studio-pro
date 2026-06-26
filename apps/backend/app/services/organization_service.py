"""Organization onboarding and lookups."""

import re
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import ROLE_ORG_ADMIN
from app.integrations.clerk import ClerkUser
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User
from app.models.workspace import Workspace


class OnboardingError(Exception):
    """Raised when onboarding cannot proceed (e.g. user already onboarded)."""


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "org"


async def _unique_slug(db: AsyncSession, base: str) -> str:
    slug = base
    suffix = 1
    while True:
        exists = await db.scalar(
            select(func.count()).select_from(Organization).where(Organization.slug == slug)
        )
        if not exists:
            return slug
        suffix += 1
        slug = f"{base}-{suffix}"


async def get_organization(db: AsyncSession, organization_id: uuid.UUID) -> Organization | None:
    return await db.get(Organization, organization_id)


async def create_organization_with_owner(
    db: AsyncSession,
    clerk_user: ClerkUser,
    org_name: str,
    workspace_name: str,
) -> tuple[Organization, User]:
    """Create an organization, its first workspace, and the owning Org Admin user.

    All four storage writes happen in one transaction so onboarding is atomic.
    """
    role = await db.scalar(select(Role).where(Role.name == ROLE_ORG_ADMIN))
    if role is None:
        raise OnboardingError("Default roles are not seeded.")

    organization = Organization(
        name=org_name,
        slug=await _unique_slug(db, _slugify(org_name)),
    )
    db.add(organization)
    await db.flush()  # assign organization.id

    db.add(Workspace(organization_id=organization.id, name=workspace_name))

    user = User(
        clerk_user_id=clerk_user.clerk_user_id,
        organization_id=organization.id,
        role_id=role.id,
        email=clerk_user.email,
        full_name=clerk_user.full_name,
    )
    db.add(user)

    await db.commit()
    await db.refresh(organization)
    await db.refresh(user)
    return organization, user

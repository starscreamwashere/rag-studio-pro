"""seed default RBAC roles

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-26 18:15:00.000000
"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.core.permissions import DEFAULT_ROLES

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

roles_table = sa.table(
    "roles",
    sa.column("id", sa.Uuid),
    sa.column("name", sa.String),
    sa.column("permissions", postgresql.JSONB),
)


def upgrade() -> None:
    op.bulk_insert(
        roles_table,
        [
            {"id": uuid.uuid4(), "name": name, "permissions": permissions}
            for name, permissions in DEFAULT_ROLES.items()
        ],
    )


def downgrade() -> None:
    op.execute(roles_table.delete().where(roles_table.c.name.in_(list(DEFAULT_ROLES.keys()))))

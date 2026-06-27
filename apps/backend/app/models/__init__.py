"""ORM models.

Importing them here ensures they are registered on ``Base.metadata`` so
Alembic autogenerate and ``create_all`` see every table.
"""

from app.models.document import Document
from app.models.ingestion_job import IngestionJob
from app.models.knowledge_base import KnowledgeBase
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User
from app.models.workspace import Workspace

__all__ = [
    "Organization",
    "Workspace",
    "Role",
    "User",
    "KnowledgeBase",
    "Document",
    "IngestionJob",
]

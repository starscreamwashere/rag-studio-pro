"""Knowledge Base — a logical retrieval collection within a workspace."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.workspace import Workspace


class KnowledgeBase(UUIDPrimaryKey, TimestampMixin, Base):
    __tablename__ = "knowledge_bases"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Retrieval config — consumed in later phases; defaults are fine for now.
    embedding_model: Mapped[str] = mapped_column(String(100), nullable=False, default="minilm")
    retrieval_default: Mapped[str] = mapped_column(String(50), nullable=False, default="vector")
    # recursive | semantic (Phase 6) — applied at ingestion time
    chunking_strategy: Mapped[str] = mapped_column(String(20), nullable=False, default="recursive")
    # active | syncing | failed | archived
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    workspace: Mapped[Workspace] = relationship()
    documents: Mapped[list[Document]] = relationship(
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
    )

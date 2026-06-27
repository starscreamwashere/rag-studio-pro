"""Chunk — metadata registry for a slice of a document.

The embedding vector and the chunk text live in Qdrant (``vector_id`` is the
Qdrant point id); Postgres keeps only metadata. ``graph_node_ids`` is populated
in Phase 5 (Graph RAG).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import UUIDPrimaryKey

if TYPE_CHECKING:
    from app.models.document import Document


class Chunk(UUIDPrimaryKey, Base):
    __tablename__ = "chunks"

    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Qdrant point id (== str(this chunk's id)).
    vector_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # Populated in Phase 5 (Graph RAG); list of Neo4j node ids.
    graph_node_ids: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    document: Mapped[Document] = relationship(back_populates="chunks")

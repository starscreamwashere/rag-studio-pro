"""Chat session — a conversation container (Assistant Mode).

Bound to one knowledge base: retrieval must stay within a single embedding
space, so a conversation targets a single KB.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.models.message import Message


class ChatSession(UUIDPrimaryKey, TimestampMixin, Base):
    __tablename__ = "chat_sessions"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    knowledge_base_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("knowledge_bases.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="New chat")

    messages: Mapped[list[Message]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

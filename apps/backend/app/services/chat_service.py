"""Chat session + message persistence."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_session import ChatSession
from app.models.message import Message


async def create_session(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    workspace_id: uuid.UUID,
    knowledge_base_id: uuid.UUID,
    title: str | None,
) -> ChatSession:
    session = ChatSession(
        user_id=user_id,
        workspace_id=workspace_id,
        knowledge_base_id=knowledge_base_id,
        title=title or "New chat",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def list_for_user(db: AsyncSession, user_id: uuid.UUID) -> list[tuple[ChatSession, int]]:
    stmt = (
        select(ChatSession, func.count(Message.id))
        .outerjoin(Message, Message.chat_session_id == ChatSession.id)
        .where(ChatSession.user_id == user_id)
        .group_by(ChatSession.id)
        .order_by(ChatSession.updated_at.desc())
    )
    return [(row[0], row[1]) for row in (await db.execute(stmt)).all()]


async def get_for_user(
    db: AsyncSession, session_id: uuid.UUID, user_id: uuid.UUID
) -> ChatSession | None:
    stmt = select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id)
    return (await db.execute(stmt)).scalar_one_or_none()


async def get_messages(db: AsyncSession, session_id: uuid.UUID) -> list[Message]:
    stmt = select(Message).where(Message.chat_session_id == session_id).order_by(Message.created_at)
    return list((await db.execute(stmt)).scalars().all())


async def recent_history(
    db: AsyncSession, session_id: uuid.UUID, limit: int = 6
) -> list[tuple[str, str]]:
    """Most recent prior turns as (role, content), chronological order."""
    stmt = (
        select(Message.role, Message.content)
        .where(Message.chat_session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    rows = (await db.execute(stmt)).all()
    return [(r[0], r[1]) for r in reversed(rows)]


async def add_message(
    db: AsyncSession,
    *,
    session_id: uuid.UUID,
    role: str,
    content: str,
    citations: list | None = None,
    confidence: float | None = None,
) -> Message:
    msg = Message(
        chat_session_id=session_id,
        role=role,
        content=content,
        citations_json=citations,
        confidence_score=confidence,
    )
    db.add(msg)
    # Touch the session so it sorts to the top of the history list.
    session = await db.get(ChatSession, session_id)
    if session is not None:
        session.updated_at = func.now()
    await db.commit()
    await db.refresh(msg)
    return msg


async def set_title(db: AsyncSession, session: ChatSession, title: str) -> None:
    session.title = title[:255]
    await db.commit()


async def delete_session(db: AsyncSession, session: ChatSession) -> None:
    await db.delete(session)
    await db.commit()

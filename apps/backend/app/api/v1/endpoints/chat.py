"""Chat Assistant endpoints: sessions, history, and streaming RAG replies."""

import json
import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.deps import CurrentUser, DbSession
from app.core import ratelimit
from app.db.session import SessionLocal
from app.integrations import llm
from app.integrations.llm import LLMError, LLMNotConfigured
from app.models.message import Message
from app.rag import generation, retrieval
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionDetail,
    ChatSessionRead,
    MessageRead,
    SendMessageRequest,
)
from app.services import chat_service, document_service
from app.services import knowledge_base_service as kb_service

router = APIRouter(prefix="/chat", tags=["chat"])


def _message_read(msg: Message) -> MessageRead:
    return MessageRead(
        id=msg.id,
        role=msg.role,
        content=msg.content,
        citations=msg.citations_json,
        confidence_score=msg.confidence_score,
        created_at=msg.created_at,
    )


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("/sessions", response_model=ChatSessionRead, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: ChatSessionCreate, user: CurrentUser, db: DbSession
) -> ChatSessionRead:
    kb = await kb_service.get_for_org(db, payload.knowledge_base_id, user.organization_id)
    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found"
        )
    session = await chat_service.create_session(
        db,
        user_id=user.id,
        workspace_id=kb.workspace_id,
        knowledge_base_id=kb.id,
        title=payload.title,
    )
    return ChatSessionRead.model_validate(session)


@router.get("/sessions", response_model=list[ChatSessionRead])
async def list_sessions(user: CurrentUser, db: DbSession) -> list[ChatSessionRead]:
    out = []
    for session, count in await chat_service.list_for_user(db, user.id):
        read = ChatSessionRead.model_validate(session)
        read.message_count = count
        out.append(read)
    return out


@router.get("/sessions/{session_id}", response_model=ChatSessionDetail)
async def get_session(session_id: uuid.UUID, user: CurrentUser, db: DbSession) -> ChatSessionDetail:
    session = await chat_service.get_for_user(db, session_id, user.id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    messages = await chat_service.get_messages(db, session_id)
    # Build from ChatSessionRead (no relationship fields) to avoid an async lazy
    # load of session.messages; attach the explicitly-fetched messages.
    read = ChatSessionRead.model_validate(session)
    return ChatSessionDetail(
        **read.model_dump(exclude={"message_count"}),
        message_count=len(messages),
        messages=[_message_read(m) for m in messages],
    )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: uuid.UUID, user: CurrentUser, db: DbSession) -> None:
    session = await chat_service.get_for_user(db, session_id, user.id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    await chat_service.delete_session(db, session)


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: uuid.UUID, payload: SendMessageRequest, user: CurrentUser, db: DbSession
) -> StreamingResponse:
    session = await chat_service.get_for_user(db, session_id, user.id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if session.knowledge_base_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This chat's knowledge base is no longer available.",
        )
    kb = await kb_service.get_for_org(db, session.knowledge_base_id, user.organization_id)
    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This chat's knowledge base is no longer available.",
        )

    await ratelimit.enforce(user)
    # Prior turns (before this question), then persist the user turn.
    history = await chat_service.recent_history(db, session_id)
    await chat_service.add_message(db, session_id=session_id, role="user", content=payload.content)
    if not history:  # first turn → title from the question
        await chat_service.set_title(db, session, payload.content)

    chunks = await retrieval.retrieve(kb, payload.content)
    names = await document_service.file_names_for(
        db, [uuid.UUID(d) for d in {c.document_id for c in chunks} if d]
    )
    citations = generation.build_citations(chunks, names)
    confidence = generation.confidence(chunks)
    prompt = generation.build_chat_prompt(payload.content, chunks, history)

    async def event_stream() -> AsyncIterator[str]:
        # Citations up front so the UI can render source cards immediately.
        yield _sse("meta", {"citations": citations, "confidence": confidence})
        parts: list[str] = []
        error: str | None = None
        try:
            async for token in llm.stream(prompt, generation.SYSTEM_PROMPT):
                parts.append(token)
                yield _sse("token", {"text": token})
        except LLMNotConfigured:
            error = "No LLM provider is configured."
        except LLMError as exc:
            error = str(exc)
        if error:
            yield _sse("error", {"detail": error})

        answer = "".join(parts)
        # Persist the assistant turn in a fresh session (the request session is closed).
        async with SessionLocal() as s:
            msg = await chat_service.add_message(
                s,
                session_id=session_id,
                role="assistant",
                content=answer,
                citations=citations,
                confidence=confidence,
            )
            message_id = str(msg.id)
        yield _sse("done", {"message_id": message_id})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

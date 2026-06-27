"""Agentic chat endpoint (Phase 7).

Runs the LangGraph agent over a chat session: autonomous tool selection,
multi-hop retrieval, optional web search (human-approved), with the session's
recent history as memory. Returns the answer plus the reasoning/tool trace.
"""

import uuid

from fastapi import APIRouter, HTTPException, status

from app.agent.graph import run_agent
from app.api.deps import CurrentUser, DbSession
from app.core import ratelimit
from app.integrations import llm
from app.schemas.agent import AgentMessageRequest, AgentResponse, AgentSource
from app.services import audit_service, chat_service, document_service
from app.services import knowledge_base_service as kb_service

router = APIRouter(prefix="/chat", tags=["agent"])


@router.post("/sessions/{session_id}/agent", response_model=AgentResponse)
async def agent_message(
    session_id: uuid.UUID,
    payload: AgentMessageRequest,
    user: CurrentUser,
    db: DbSession,
) -> AgentResponse:
    session = await chat_service.get_for_user(db, session_id, user.id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if session.knowledge_base_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No knowledge base.")
    kb = await kb_service.get_for_org(db, session.knowledge_base_id, user.organization_id)
    if kb is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No knowledge base.")

    await ratelimit.enforce(user)
    history = await chat_service.recent_history(db, session_id)
    await chat_service.add_message(db, session_id=session_id, role="user", content=payload.content)
    if not history:
        await chat_service.set_title(db, session, payload.content)

    state = await run_agent(kb, payload.content, history, payload.allow_web_search)

    # Build citations from retrieved chunks (works for vector + hybrid chunk types).
    chunks = state.get("chunks", [])
    doc_ids = [uuid.UUID(c.document_id) for c in chunks if getattr(c, "document_id", "")]
    names = await document_service.file_names_for(db, doc_ids)
    sources: list[AgentSource] = []
    scores: list[float] = []
    for i, c in enumerate(chunks):
        score = getattr(c, "fused_score", None) or getattr(c, "score", 0.0)
        scores.append(getattr(c, "vector_score", None) or getattr(c, "score", 0.0) or 0.0)
        sources.append(
            AgentSource(
                index=i + 1,
                document_id=c.document_id,
                file_name=names.get(c.document_id, "unknown"),
                score=round(float(score), 4),
                snippet=c.text[:240],
            )
        )
    confidence = round(sum(scores) / len(scores), 4) if scores else None

    msg = await chat_service.add_message(
        db,
        session_id=session_id,
        role="assistant",
        content=state.get("answer", ""),
        citations=[s.model_dump() for s in sources],
        confidence=confidence,
    )

    tools_used = sorted({str(t.get("node")) for t in state.get("trace", [])})
    await audit_service.log(
        db,
        organization_id=user.organization_id,
        actor_id=user.id,
        action="agent.query",
        resource_type="chat_session",
        resource_id=str(session_id),
        metadata={"tools": tools_used, "needs_approval": bool(state.get("needs_approval"))},
    )

    return AgentResponse(
        message_id=msg.id,
        answer=state.get("answer", ""),
        trace=state.get("trace", []),
        sources=sources,
        confidence=confidence,
        needs_approval=bool(state.get("needs_approval")),
        model=llm.active_model(),
        llm_configured=llm.is_configured(),
        generation_error=state.get("generation_error"),
    )

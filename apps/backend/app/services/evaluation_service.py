"""Evaluation run persistence (Studio experiments)."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluation_run import EvaluationRun


async def create_run(db: AsyncSession, **fields) -> EvaluationRun:
    run = EvaluationRun(**fields)
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


async def list_for_workspace(
    db: AsyncSession, workspace_id: uuid.UUID, limit: int = 50
) -> list[EvaluationRun]:
    stmt = (
        select(EvaluationRun)
        .where(EvaluationRun.workspace_id == workspace_id)
        .order_by(EvaluationRun.created_at.desc())
        .limit(limit)
    )
    return list((await db.execute(stmt)).scalars().all())

"""Celery application (Redis broker + result backend).

Phase 0 wires the worker so the queue is reachable. Real tasks (document
ingestion, embedding generation, graph extraction, batch evaluation) are
registered in their respective phases.
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "ragstudio",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.worker.tasks.ingestion"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    timezone="UTC",
)


@celery_app.task(name="ping")
def ping() -> str:
    """Trivial task to verify the worker is alive."""
    return "pong"

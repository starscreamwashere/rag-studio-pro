"""Document ingestion task (Phase 2: parse + store parsed text).

Later phases extend this pipeline with chunking, embedding, graph extraction,
and indexing steps.
"""

import uuid
from datetime import UTC, datetime

from app.core.config import settings
from app.db.sync_session import SyncSessionLocal
from app.ingestion.parsers import parse
from app.integrations import storage
from app.models.document import Document
from app.models.ingestion_job import IngestionJob
from app.worker.celery_app import celery_app


def _now() -> datetime:
    return datetime.now(UTC)


@celery_app.task(name="ingest_document")
def ingest_document(document_id: str, job_id: str) -> str:
    with SyncSessionLocal() as db:
        doc = db.get(Document, uuid.UUID(document_id))
        job = db.get(IngestionJob, uuid.UUID(job_id))
        if doc is None or job is None:
            return "missing"

        try:
            job.status = "processing"
            job.current_step = "parsing"
            job.progress_percent = 20
            job.started_at = _now()
            doc.ingestion_status = "processing"
            db.commit()

            data = storage.download_bytes(settings.minio_documents_bucket, doc.storage_url)
            parsed = parse(data, doc.file_type)

            parsed_key = f"{doc.knowledge_base_id}/{doc.id}/parsed.txt"
            storage.upload_bytes(
                settings.minio_documents_bucket,
                parsed_key,
                parsed.text.encode("utf-8"),
                "text/plain; charset=utf-8",
            )

            job.status = "completed"
            job.current_step = "parsed"
            job.progress_percent = 100
            job.finished_at = _now()
            doc.ingestion_status = "completed"
            db.commit()
            return "completed"
        except Exception as exc:  # noqa: BLE001 — record any failure on the job
            db.rollback()
            job = db.get(IngestionJob, uuid.UUID(job_id))
            doc = db.get(Document, uuid.UUID(document_id))
            if job is not None:
                job.status = "failed"
                job.error_message = str(exc)[:1000]
                job.finished_at = _now()
            if doc is not None:
                doc.ingestion_status = "failed"
            db.commit()
            return "failed"

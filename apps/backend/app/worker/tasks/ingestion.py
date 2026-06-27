"""Document ingestion task.

Pipeline: parse -> store parsed text -> chunk -> embed -> index in Qdrant,
tracking each step on the IngestionJob. Later phases add graph extraction.
"""

import uuid
from datetime import UTC, datetime

from app.core.config import settings
from app.db.sync_session import SyncSessionLocal
from app.ingestion.parsers import parse
from app.integrations import storage
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.ingestion_job import IngestionJob
from app.models.knowledge_base import KnowledgeBase
from app.rag import embeddings, vector_store
from app.rag.chunking import chunk_text, count_tokens
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
        kb = db.get(KnowledgeBase, doc.knowledge_base_id)
        if kb is None:
            return "missing"

        try:
            job.status = "processing"
            job.current_step = "parsing"
            job.progress_percent = 20
            job.started_at = _now()
            doc.ingestion_status = "processing"
            db.commit()

            # Parse + persist cleaned text.
            data = storage.download_bytes(settings.minio_documents_bucket, doc.storage_url)
            parsed = parse(data, doc.file_type)
            storage.upload_bytes(
                settings.minio_documents_bucket,
                f"{doc.knowledge_base_id}/{doc.id}/parsed.txt",
                parsed.text.encode("utf-8"),
                "text/plain; charset=utf-8",
            )

            # Chunk.
            job.current_step = "chunking"
            job.progress_percent = 40
            db.commit()
            texts = chunk_text(parsed.text)
            chunk_rows: list[tuple[Chunk, str]] = []
            for i, text in enumerate(texts):
                chunk = Chunk(document_id=doc.id, chunk_index=i, token_count=count_tokens(text))
                db.add(chunk)
                chunk_rows.append((chunk, text))
            db.flush()

            # Embed.
            job.current_step = "embedding"
            job.progress_percent = 70
            db.commit()
            vectors = embeddings.embed_texts(kb.embedding_model, [t for _, t in chunk_rows])

            # Index in Qdrant.
            job.current_step = "indexing"
            job.progress_percent = 90
            db.commit()
            collection = vector_store.collection_name(kb.id)
            vector_store.ensure_collection(
                collection, embeddings.get_dimensions(kb.embedding_model)
            )
            points = []
            for (chunk, text), vector in zip(chunk_rows, vectors, strict=True):
                chunk.vector_id = str(chunk.id)
                points.append(
                    {
                        "id": str(chunk.id),
                        "vector": vector,
                        "payload": {
                            "chunk_id": str(chunk.id),
                            "document_id": str(doc.id),
                            "knowledge_base_id": str(kb.id),
                            "workspace_id": str(kb.workspace_id),
                            "chunk_index": chunk.chunk_index,
                            "text": text,
                        },
                    }
                )
            if points:
                vector_store.upsert_points(collection, points)

            job.status = "completed"
            job.current_step = "indexed"
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

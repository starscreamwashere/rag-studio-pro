"""Synchronous DB session for the Celery worker.

Celery tasks run synchronously, so they use a plain (non-async) SQLAlchemy
session. psycopg3 backs both the async engine and this sync engine off the
same DATABASE_URL.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

sync_engine = create_engine(settings.database_url, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)

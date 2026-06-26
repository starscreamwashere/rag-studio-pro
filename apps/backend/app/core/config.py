"""Application settings, sourced from environment variables.

Storage boundaries are explicit here (Postgres / Qdrant / Neo4j / MinIO /
Redis) and are wired up in their respective phases. In Phase 0 these values
exist so the stack can connect, but no service depends on them yet.
"""

import base64
import binascii
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "RAG Studio Pro"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    # CORS — the Next.js frontend origin.
    cors_origins: list[str] = ["http://localhost:3000"]

    # Clerk authentication
    clerk_secret_key: str = ""
    clerk_publishable_key: str = ""
    # Optional explicit overrides; otherwise derived from the publishable key.
    clerk_jwks_url: str = ""
    clerk_issuer: str = ""

    # PostgreSQL (relational / tenant data)
    database_url: str = "postgresql+psycopg://ragstudio:ragstudio@postgres:5432/ragstudio"

    # Redis (cache + Celery broker)
    redis_url: str = "redis://redis:6379/0"

    # Qdrant (vectors)
    qdrant_url: str = "http://qdrant:6333"

    # Neo4j (knowledge graph)
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "ragstudio123"

    # MinIO (object storage)
    minio_endpoint: str = "http://minio:9000"
    minio_root_user: str = "ragstudio"
    minio_root_password: str = "ragstudio123"

    # Providers (populated per phase)
    gemini_api_key: str = ""
    groq_api_key: str = ""
    anthropic_api_key: str = ""
    langsmith_api_key: str = ""

    @property
    def clerk_frontend_api(self) -> str:
        """Decode the Clerk Frontend API host from the publishable key.

        Publishable keys look like ``pk_test_<base64(host + '$')>``; the decoded
        host (e.g. ``relaxed-cat-12.clerk.accounts.dev``) is the JWT issuer and
        the source of the JWKS endpoint.
        """
        key = self.clerk_publishable_key
        if not key:
            return ""
        encoded = key.removeprefix("pk_test_").removeprefix("pk_live_")
        try:
            decoded = base64.b64decode(encoded + "==").decode("utf-8")
        except (binascii.Error, UnicodeDecodeError):
            return ""
        return decoded.rstrip("$")

    @property
    def clerk_issuer_url(self) -> str:
        if self.clerk_issuer:
            return self.clerk_issuer
        host = self.clerk_frontend_api
        return f"https://{host}" if host else ""

    @property
    def clerk_jwks_uri(self) -> str:
        if self.clerk_jwks_url:
            return self.clerk_jwks_url
        issuer = self.clerk_issuer_url
        return f"{issuer}/.well-known/jwks.json" if issuer else ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

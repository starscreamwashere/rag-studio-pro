"""FastAPI application entrypoint."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app import __version__
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import settings


def _configure_langsmith() -> None:
    """Enable LangSmith tracing for LangGraph runs when a key is configured."""
    if settings.langsmith_api_key:
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
        os.environ.setdefault("LANGCHAIN_API_KEY", settings.langsmith_api_key)
        os.environ.setdefault("LANGCHAIN_PROJECT", settings.langsmith_project)


def create_app() -> FastAPI:
    _configure_langsmith()
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="Advanced Multi-Modal Intelligent RAG Platform.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Unversioned probe endpoint for container / load-balancer health checks.
    app.include_router(health_router)
    # Versioned API surface.
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    # Prometheus metrics at /metrics (default request count/latency + custom metrics).
    Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

    @app.get("/", tags=["root"])
    def root() -> dict[str, str]:
        return {
            "name": settings.app_name,
            "version": __version__,
            "docs": "/docs",
        }

    return app


app = create_app()

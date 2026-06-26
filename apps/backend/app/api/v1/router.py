"""Aggregates all v1 endpoint routers.

As later phases add modules (auth, knowledge bases, ingestion, retrieval,
chat, evaluation, admin, analytics), include their routers here.
"""

from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])

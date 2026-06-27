"""Aggregates all v1 endpoint routers.

As later phases add modules (knowledge bases, ingestion, retrieval, chat,
evaluation, admin, analytics), include their routers here.
"""

from fastapi import APIRouter

from app.api.v1.endpoints.agent import router as agent_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.documents import router as documents_router
from app.api.v1.endpoints.graph import router as graph_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.knowledge_bases import router as knowledge_bases_router
from app.api.v1.endpoints.organizations import router as organizations_router
from app.api.v1.endpoints.query import router as query_router
from app.api.v1.endpoints.studio import router as studio_router
from app.api.v1.endpoints.workspaces import router as workspaces_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router)
api_router.include_router(organizations_router)
api_router.include_router(workspaces_router)
api_router.include_router(knowledge_bases_router)
api_router.include_router(documents_router)
api_router.include_router(query_router)
api_router.include_router(graph_router)
api_router.include_router(chat_router)
api_router.include_router(agent_router)
api_router.include_router(studio_router)

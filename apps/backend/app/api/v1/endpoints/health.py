"""Health endpoints.

Phase 0 acceptance: the backend health endpoint works. Deeper readiness
probes (pinging each storage layer) are added as those connections come
online in later phases.
"""

from fastapi import APIRouter

from app import __version__

router = APIRouter()


@router.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok", "version": __version__}

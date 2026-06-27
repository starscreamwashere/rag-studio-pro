"""Redis-backed rate limiting + per-organization daily quota.

Called at the top of expensive LLM endpoints (chat, agent, query, studio).
Fixed-window counters keep it simple and dependency-free beyond Redis.
"""

from datetime import UTC, datetime

from fastapi import HTTPException, status
from redis.asyncio import Redis

from app.core import metrics
from app.core.config import settings
from app.models.user import User

_redis: Redis | None = None


def _client() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def enforce(user: User) -> None:
    """Raise 429 if the user's per-minute rate or the org's daily quota is exceeded."""
    r = _client()
    now = datetime.now(UTC)

    minute_key = f"rl:{user.id}:{now:%Y%m%d%H%M}"
    count = await r.incr(minute_key)
    if count == 1:
        await r.expire(minute_key, 60)
    if count > settings.rate_limit_per_minute:
        metrics.rate_limit_rejections_total.labels("rate_limit").inc()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please slow down.",
        )

    quota_key = f"quota:{user.organization_id}:{now:%Y%m%d}"
    used = await r.incr(quota_key)
    if used == 1:
        await r.expire(quota_key, 86400)
    if used > settings.org_daily_quota:
        metrics.rate_limit_rejections_total.labels("quota").inc()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily organization quota exceeded.",
        )

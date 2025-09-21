"""FastAPI dependency providers."""

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache_service import CacheService
from app.core.config import settings
from app.core.metrics_collector import MetricsCollector
from app.infra.db import get_session


async def get_redis_connection() -> Redis:
    """Get Redis connection."""
    redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
    )
    try:
        yield redis
    finally:
        await redis.aclose()


# Cache service provider
def get_cache_service(
    redis: Redis = Depends(get_redis_connection),
) -> CacheService:
    """Get cache service."""
    return CacheService(redis)


# Metrics collector provider
def get_metrics_collector(
    redis: Redis = Depends(get_redis_connection),
    session: AsyncSession = Depends(get_session),
) -> MetricsCollector:
    """Get metrics collector."""
    return MetricsCollector(redis, lambda: session)

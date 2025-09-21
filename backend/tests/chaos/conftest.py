"""Test fixtures for quality metrics chaos tests."""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache_service import CacheService
from app.core.metrics_collector import MetricsCollector
from tests.conftest import app, async_client, db_session


@pytest_asyncio.fixture
async def redis() -> AsyncGenerator[Redis, None]:
    """Create Redis connection for tests."""
    # Use test Redis DB
    redis = Redis(host="localhost", port=6379, db=1)
    await redis.flushdb()  # Clear test DB
    yield redis
    await redis.flushdb()  # Clean up
    await redis.aclose()


@pytest_asyncio.fixture
async def cache_service(redis: Redis) -> AsyncGenerator[CacheService, None]:
    """Create cache service for tests."""
    service = CacheService(redis, prefix="test")
    yield service


@pytest_asyncio.fixture
async def metrics_collector(
    redis: Redis, db_session: AsyncSession
) -> AsyncGenerator[MetricsCollector, None]:
    """Create metrics collector for tests."""
    collector = MetricsCollector(redis, lambda: db_session)
    yield collector


@pytest_asyncio.fixture
async def chaos_app(
    app, cache_service: CacheService, metrics_collector: MetricsCollector
):
    """Configure FastAPI app with chaos test dependencies."""
    from app.core.dependencies import get_cache_service, get_metrics_collector

    # Override dependencies
    app.dependency_overrides[get_cache_service] = lambda: cache_service
    app.dependency_overrides[get_metrics_collector] = lambda: metrics_collector

    yield app

    # Clean up
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def chaos_client(
    chaos_app,
    db_session: AsyncSession,
    cache_service: CacheService,
    metrics_collector: MetricsCollector,
) -> AsyncGenerator[AsyncClient, None]:
    """Create test client for chaos tests."""
    async with AsyncClient(
        app=chaos_app,
        base_url="http://test",
        follow_redirects=True,
    ) as client:
        # Start collector in background
        collection_task = asyncio.create_task(metrics_collector.start())
        yield client
        # Clean up
        await metrics_collector.stop()
        await collection_task

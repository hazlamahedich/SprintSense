"""Configuration and fixtures for chaos testing."""

from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.metrics_logger import metrics_logger
from app.services.recommendations_service import RecommendationsService

# Mock services for testing
mock_metrics_logger = metrics_logger
mock_recommendations_service = RecommendationsService


@pytest.fixture
async def chaos_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a session with chaos conditions enabled."""
    async with AsyncSession(expire_on_commit=False) as session:
        await session.execute("SELECT pg_advisory_lock(1)")  # Enable chaos mode
        try:
            yield session
        finally:
            await session.execute("SELECT pg_advisory_unlock(1)")
            await session.rollback()


@pytest.fixture
async def chaos_service(chaos_session) -> AsyncGenerator[RecommendationsService, None]:
    """Get a recommendations service with chaos conditions enabled."""
    service = RecommendationsService(
        metrics_logger=mock_metrics_logger,
        session=chaos_session,
    )
    try:
        yield service
    finally:
        await service.reset_chaos_conditions()

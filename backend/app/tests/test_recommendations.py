"""Tests for recommendations functionality."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.ai_service import AIService
from app.core.metrics_logger import metrics_logger
from app.services.recommendations_service import RecommendationsService


@pytest.fixture
def mock_cache():
    """Mock cache service."""
    cache = MagicMock()
    cache.get = AsyncMock()
    cache.set = AsyncMock()
    return cache


@pytest.fixture
def mock_ai_service():
    """Mock AI service."""
    service = MagicMock(spec=AIService)
    service.generate_recommendations = AsyncMock()
    return service


@pytest.fixture
def recommendations_service(mock_cache, mock_ai_service):
    """Get a recommendations service with mocked dependencies."""
    return RecommendationsService(
        cache=mock_cache,
        ai_service=mock_ai_service,
        metrics_logger=metrics_logger,
    )


@pytest.mark.asyncio
async def test_get_cached_recommendations(
    recommendations_service: RecommendationsService,
    mock_cache: MagicMock,
):
    """Test retrieving cached recommendations."""
    # Setup
    cached_recommendations = {
        "items": [{"id": "1", "score": 0.95}],
        "timestamp": datetime.now().isoformat(),
    }
    mock_cache.get.return_value = cached_recommendations

    # Execute
    result = await recommendations_service.get_recommendations()

    # Verify cache was checked and recommendations were returned
    pytest.fail_if(
        result != cached_recommendations, "Result did not match cached recommendations"
    )
    pytest.fail_if(
        mock_cache.get.call_count != 1, "Cache get method was not called exactly once"
    )


@pytest.mark.asyncio
async def test_generate_new_recommendations(
    recommendations_service: RecommendationsService,
    mock_cache: MagicMock,
    mock_ai_service: MagicMock,
):
    """Test generating new recommendations when cache is empty."""
    # Setup
    mock_cache.get.return_value = None
    ai_recommendations = {
        "items": [{"id": "1", "score": 0.85}],
        "timestamp": datetime.now().isoformat(),
    }
    mock_ai_service.generate_recommendations.return_value = ai_recommendations

    # Execute
    result = await recommendations_service.get_recommendations()

    # Verify AI service was called and recommendations were cached
    pytest.fail_if(
        result != ai_recommendations, "Result did not match AI service recommendations"
    )
    pytest.fail_if(
        mock_ai_service.generate_recommendations.call_count != 1,
        "AI service generate method was not called exactly once",
    )


@pytest.mark.asyncio
async def test_velocity_metrics_calculation(
    recommendations_service: RecommendationsService,
):
    """Test calculation of team velocity metrics."""
    # Setup test data
    completed_items = [
        {
            "story_points": 5,
            "completed_at": datetime.now() - timedelta(days=1),
            "started_at": datetime.now() - timedelta(days=3),
        },
        {
            "story_points": 3,
            "completed_at": datetime.now() - timedelta(days=2),
            "started_at": datetime.now() - timedelta(days=4),
        },
    ]

    # Calculate velocity metrics
    velocity_metrics = recommendations_service.calculate_velocity_metrics(
        completed_items
    )

    # Verify velocity metrics exist
    for metric in ["story_points_velocity", "avg_completion_time", "completion_rate"]:
        pytest.fail_if(
            metric not in velocity_metrics, f"Missing required metric: {metric}"
        )

    # Verify completion rate is positive
    pytest.fail_if(
        velocity_metrics["completion_rate"] <= 0,
        "Completion rate should be greater than zero",
    )


@pytest.mark.asyncio
async def test_error_handling(
    recommendations_service: RecommendationsService,
    mock_ai_service: MagicMock,
):
    """Test error handling when AI service fails."""
    # Setup
    expected_error = "Failed to generate recommendations"
    mock_ai_service.generate_recommendations.side_effect = Exception(expected_error)

    # Execute and verify error handling
    with pytest.raises(Exception) as exc_info:
        await recommendations_service.get_recommendations()
        pytest.fail_if(
            expected_error not in str(exc_info.value),
            f"Expected error message '{expected_error}' not found in exception",
        )

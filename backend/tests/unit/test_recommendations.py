import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import AsyncSession
from app.services.recommendations_service import RecommendationsService
from app.domains.models.work_item import WorkItem
from app.schemas.recommendation import WorkItemRecommendation


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_cache():
    return AsyncMock()


@pytest.fixture
def mock_ai_service():
    return AsyncMock()


@pytest.fixture
def mock_circuit_breaker():
    return AsyncMock(
        __aenter__=AsyncMock(),
        __aexit__=AsyncMock(),
    )


@pytest_asyncio.fixture
async def recommendations_service(mock_cache, mock_ai_service, mock_circuit_breaker):
    with (
        patch("app.services.recommendations_service.AsyncCache") as mock_cache_cls,
        patch("app.services.recommendations_service.AIService") as mock_ai_cls,
        patch("app.services.recommendations_service.CircuitBreaker") as mock_cb_cls,
    ):

        mock_cache_cls.return_value = mock_cache
        mock_ai_cls.return_value = mock_ai_service
        mock_cb_cls.return_value = mock_circuit_breaker

        service = RecommendationsService()
        yield service


@pytest.fixture
def mock_work_items():
    now = datetime.utcnow()
    return [
        WorkItem(
            id=f"item_{i}",
            team_id="team123",
            type="story",
            title=f"Test Item {i}",
            description=f"Description {i}",
            story_points=i,
            created_at=now - timedelta(days=i),
            completed_at=now if i % 2 == 0 else None,
            author_id="user123",  # Required field
        )
        for i in range(10)
    ]


@pytest.mark.asyncio
async def test_get_recommendations_from_cache(
    recommendations_service, mock_session, mock_cache
):
    # Setup cached recommendations
    cached_recommendations = [
        WorkItemRecommendation(
            id="rec_1",
            title="Cached Recommendation",
            description="Test description",
            type="story",
            suggested_priority=0.8,
            confidence_scores={"title": 0.9, "priority": 0.8},
            reasoning="Test reasoning",
            patterns_identified=["test_pattern"],
            team_velocity_factor=0.75,
        )
    ]
    mock_cache.get.return_value = cached_recommendations

    # Get recommendations
    result = await recommendations_service.get_recommendations(mock_session, "team123")

    # Verify cache was checked and recommendations were returned
    assert result == cached_recommendations
    mock_cache.get.assert_called_once()
    mock_session.execute.assert_not_called()


@pytest.mark.asyncio
async def test_get_recommendations_from_ai_service(
    recommendations_service, mock_session, mock_cache, mock_ai_service, mock_work_items
):
    # Setup cache miss
    mock_cache.get.return_value = None

    # Setup mock session response with sync-like result API
    class _Scalars:
        def __init__(self, items):
            self._items = items

        def all(self):
            return self._items

    class _Result:
        def __init__(self, items):
            self._items = items

        def scalars(self):
            return _Scalars(self._items)

    mock_session.execute.return_value = _Result(mock_work_items)

    # Setup AI service response
    ai_recommendations = [
        WorkItemRecommendation(
            id="rec_1",
            title="AI Recommendation",
            description="Test description",
            type="story",
            suggested_priority=0.8,
            confidence_scores={"title": 0.9, "priority": 0.8},
            reasoning="Test reasoning",
            patterns_identified=["test_pattern"],
            team_velocity_factor=0.75,
        )
    ]
    mock_ai_service.generate_recommendations.return_value = ai_recommendations

    # Get recommendations
    result = await recommendations_service.get_recommendations(mock_session, "team123")

    # Verify AI service was called and recommendations were cached
    assert result == ai_recommendations
    mock_ai_service.generate_recommendations.assert_called_once()
    mock_cache.set.assert_called_once()


@pytest.mark.asyncio
async def test_accept_recommendation(recommendations_service, mock_session, mock_cache):
    recommendation_id = "rec_123"

    # Accept recommendation
    await recommendations_service.accept_recommendation(mock_session, recommendation_id)

    # Verify feedback was recorded and cache was invalidated
    mock_cache.clear_pattern.assert_called_once_with("recommendations:*")


@pytest.mark.asyncio
async def test_provide_feedback(
    recommendations_service, mock_session, mock_ai_service, mock_cache
):
    recommendation_id = "rec_123"
    feedback_type = "not_useful"
    reason = "Not relevant"

    # Provide feedback
    await recommendations_service.provide_feedback(
        mock_session, recommendation_id, feedback_type, reason
    )

    # Verify feedback was recorded
    mock_ai_service.record_feedback.assert_called_once()
    mock_cache.clear_pattern.assert_called_once_with("recommendations:*")


@pytest.mark.asyncio
async def test_calculate_team_velocity(
    recommendations_service, mock_session, mock_work_items
):
    # Setup mock session response with sync-like result API
    class _Scalars:
        def __init__(self, items):
            self._items = items

        def all(self):
            return self._items

    class _Result:
        def __init__(self, items):
            self._items = items

        def scalars(self):
            return _Scalars(self._items)

    mock_session.execute.return_value = _Result(mock_work_items)

    # Calculate velocity
    velocity_metrics = await recommendations_service._calculate_team_velocity(
        mock_session, "team123"
    )

    # Verify velocity metrics
    assert "story_points_velocity" in velocity_metrics
    assert "avg_completion_time" in velocity_metrics
    assert "completion_rate" in velocity_metrics
    assert velocity_metrics["completion_rate"] > 0


@pytest.mark.asyncio
async def test_error_handling(
    recommendations_service, mock_session, mock_cache, mock_ai_service
):
    # Setup cache miss and AI service error
    mock_cache.get.return_value = None
    mock_ai_service.generate_recommendations.side_effect = Exception("AI service error")

    with pytest.raises(Exception) as exc_info:
        await recommendations_service.get_recommendations(mock_session, "team123")

    assert "Failed to generate recommendations" in str(exc_info.value)


"""Unit tests for AI Prioritization Service."""

import json
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError, DatabaseError, ValidationError
from app.domains.models.project_goal import ProjectGoal
from app.domains.models.team import TeamMember, TeamRole
from app.domains.models.work_item import WorkItem, WorkItemStatus, WorkItemType
from app.domains.schemas.ai_prioritization import (
    AIPrioritizationRequest,
    BusinessMetrics,
    ScoredWorkItem,
)
from app.domains.services.ai_prioritization_service import (
    AIPrioritizationService,
    CircuitBreaker,
    CircuitBreakerError,
    TextProcessor,
)


class TestTextProcessor:
    """Test cases for TextProcessor utility class."""

    def test_strip_html(self):
        """Test HTML stripping functionality."""
        # Test basic HTML tags
        html_text = "<p>Hello <strong>world</strong>!</p>"
        result = TextProcessor.strip_html(html_text)
        assert result == "Hello world!"

        # Test HTML entities
        html_entities = "&lt;test&gt; &amp; &quot;quotes&quot;"
        result = TextProcessor.strip_html(html_entities)
        assert result == '<test> & "quotes"'

        # Test empty and None inputs
        assert TextProcessor.strip_html("") == ""
        assert TextProcessor.strip_html("plain text") == "plain text"

    def test_normalize_text(self):
        """Test text normalization."""
        # Test basic normalization
        text = "  Hello   WORLD  "
        result = TextProcessor.normalize_text(text)
        assert result == "hello world"

        # Test with HTML
        html_text = "<p>Hello <strong>WORLD</strong>!</p>"
        result = TextProcessor.normalize_text(html_text)
        assert result == "hello world!"

        # Test empty input
        assert TextProcessor.normalize_text("") == ""
        assert TextProcessor.normalize_text(None) == ""

    def test_extract_keywords(self):
        """Test keyword extraction."""
        # Test normal text
        text = "Implement user authentication system"
        keywords = TextProcessor.extract_keywords(text)
        expected = {"implement", "user", "authentication", "system"}
        assert keywords == expected

        # Test with stop words
        text_with_stopwords = "The user and the system are working"
        keywords = TextProcessor.extract_keywords(text_with_stopwords)
        # Should exclude stop words like 'the', 'and', 'are'
        expected = {"user", "system", "working"}
        assert keywords == expected

        # Test short text (less than MIN_TEXT_LENGTH)
        short_text = "Hi"
        keywords = TextProcessor.extract_keywords(short_text)
        assert keywords == set()

        # Test empty text
        keywords = TextProcessor.extract_keywords("")
        assert keywords == set()

    def test_simple_stem(self):
        """Test simple stemming algorithm."""
        # Test common suffixes
        assert TextProcessor.simple_stem("running") == "runn"
        assert TextProcessor.simple_stem("tested") == "test"
        assert TextProcessor.simple_stem("better") == "bett"
        assert TextProcessor.simple_stem("quickly") == "quick"
        assert TextProcessor.simple_stem("items") == "item"

        # Test words that shouldn't be stemmed
        assert TextProcessor.simple_stem("cat") == "cat"
        assert TextProcessor.simple_stem("dog") == "dog"
        assert TextProcessor.simple_stem("a") == "a"


class TestCircuitBreaker:
    """Test cases for CircuitBreaker implementation."""

    def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in closed state."""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1)

        # Mock function that succeeds
        mock_func = MagicMock(return_value="success")

        result = breaker.call(mock_func, "arg1", keyword="kwarg1")

        assert result == "success"
        assert breaker.state == "closed"
        assert breaker.failure_count == 0
        mock_func.assert_called_once_with("arg1", keyword="kwarg1")

    def test_circuit_breaker_failure_tracking(self):
        """Test circuit breaker failure tracking."""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1)

        # Mock function that fails
        mock_func = MagicMock(side_effect=Exception("test error"))

        # First failure
        with pytest.raises(Exception, match="test error"):
            breaker.call(mock_func)

        assert breaker.failure_count == 1
        assert breaker.state == "closed"

        # Second failure - should open circuit
        with pytest.raises(Exception, match="test error"):
            breaker.call(mock_func)

        assert breaker.failure_count == 2
        assert breaker.state == "open"

    def test_circuit_breaker_open_state(self):
        """Test circuit breaker in open state."""
        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=1)

        # Force circuit open
        mock_func = MagicMock(side_effect=Exception("test error"))
        with pytest.raises(Exception):
            breaker.call(mock_func)

        assert breaker.state == "open"

        # Subsequent calls should raise CircuitBreakerError
        with pytest.raises(CircuitBreakerError, match="Circuit breaker is open"):
            breaker.call(mock_func)


@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis_mock = AsyncMock()
    redis_mock.get.return_value = None  # Default to cache miss
    redis_mock.setex.return_value = True
    return redis_mock


@pytest.fixture
def ai_service(mock_db, mock_redis):
    """AI Prioritization Service instance with mocked dependencies."""
    return AIPrioritizationService(db=mock_db, redis_client=mock_redis)


@pytest.fixture
def sample_project_goals():
    """Sample project goals for testing."""
    goal1 = ProjectGoal()
    goal1.id = uuid.uuid4()
    goal1.team_id = uuid.uuid4()
    goal1.description = "Improve user experience and performance"
    goal1.priority_weight = 8
    goal1.success_metrics = "Reduce load time by 50%"

    goal2 = ProjectGoal()
    goal2.id = uuid.uuid4()
    goal2.team_id = goal1.team_id
    goal2.description = "Enhance system security and authentication"
    goal2.priority_weight = 6
    goal2.success_metrics = "Zero security incidents"

    return [goal1, goal2]


@pytest.fixture
def sample_work_items():
    """Sample work items for testing."""
    item1 = WorkItem()
    item1.id = uuid.uuid4()
    item1.team_id = uuid.uuid4()
    item1.title = "Optimize database queries for better performance"
    item1.description = "Improve query performance and user experience"
    item1.priority = 5.0
    item1.status = WorkItemStatus.BACKLOG
    item1.type = WorkItemType.STORY

    item2 = WorkItem()
    item2.id = uuid.uuid4()
    item2.team_id = item1.team_id
    item2.title = "Implement two-factor authentication"
    item2.description = "Add security layer for user authentication"
    item2.priority = 3.0
    item2.status = WorkItemStatus.BACKLOG
    item2.type = WorkItemType.STORY

    return [item1, item2]


class TestAIPrioritizationService:
    """Test cases for AI Prioritization Service."""

    @pytest.mark.asyncio
    async def test_score_work_items_success(
        self, ai_service, mock_db, sample_project_goals, sample_work_items
    ):
        """Test successful work item scoring."""
        team_id = sample_work_items[0].team_id
        user_id = uuid.uuid4()

        # Mock team membership check
        mock_db.execute.return_value.scalar_one_or_none.return_value = MagicMock()

        # Mock database queries
        mock_db.execute.side_effect = [
            # Team membership query
            MagicMock(scalar_one_or_none=lambda: MagicMock()),
            # Project goals query
            MagicMock(scalars=lambda: MagicMock(all=lambda: sample_project_goals)),
            # Work items query
            MagicMock(scalars=lambda: MagicMock(all=lambda: sample_work_items)),
        ]

        request = AIPrioritizationRequest(
            work_item_ids=None, include_metadata=True, mode="full"
        )

        response = await ai_service.score_work_items(team_id, user_id, request)

        assert response.total_items == 2
        assert len(response.scored_items) == 2
        assert response.generation_time_ms >= 0
        assert response.business_metrics.algorithm_version == "1.0.0"

        # Check that items are properly scored
        for item in response.scored_items:
            assert isinstance(item, ScoredWorkItem)
            assert 0.0 <= item.ai_score <= 10.0
            assert item.suggested_rank > 0
            assert item.confidence_level in ["high", "medium", "low"]
            assert len(item.explanation) > 0

    @pytest.mark.asyncio
    async def test_score_work_items_not_team_member(self, ai_service, mock_db):
        """Test scoring when user is not a team member."""
        team_id = uuid.uuid4()
        user_id = uuid.uuid4()

        # Mock no team membership
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        request = AIPrioritizationRequest(mode="full")

        with pytest.raises(AuthorizationError, match="You must be a team member"):
            await ai_service.score_work_items(team_id, user_id, request)

    @pytest.mark.asyncio
    async def test_score_work_items_no_goals(self, ai_service, mock_db):
        """Test scoring when no project goals exist."""
        team_id = uuid.uuid4()
        user_id = uuid.uuid4()

        # Mock team membership and empty goals
        mock_db.execute.side_effect = [
            # Team membership query
            MagicMock(scalar_one_or_none=lambda: MagicMock()),
            # Empty project goals query
            MagicMock(scalars=lambda: MagicMock(all=lambda: [])),
        ]

        request = AIPrioritizationRequest(mode="full")

        response = await ai_service.score_work_items(team_id, user_id, request)

        assert response.total_items == 0
        assert len(response.scored_items) == 0
        assert response.warning == "no_goals_configured"

    @pytest.mark.asyncio
    async def test_score_work_items_no_work_items(
        self, ai_service, mock_db, sample_project_goals
    ):
        """Test scoring when no work items exist."""
        team_id = uuid.uuid4()
        user_id = uuid.uuid4()

        # Mock team membership, goals, but no work items
        mock_db.execute.side_effect = [
            # Team membership query
            MagicMock(scalar_one_or_none=lambda: MagicMock()),
            # Project goals query
            MagicMock(scalars=lambda: MagicMock(all=lambda: sample_project_goals)),
            # Empty work items query
            MagicMock(scalars=lambda: MagicMock(all=lambda: [])),
        ]

        request = AIPrioritizationRequest(mode="full")

        response = await ai_service.score_work_items(team_id, user_id, request)

        assert response.total_items == 0
        assert len(response.scored_items) == 0
        assert response.warning is None

    @pytest.mark.asyncio
    async def test_redis_caching_success(
        self, ai_service, mock_db, mock_redis, sample_project_goals
    ):
        """Test Redis caching functionality."""
        team_id = uuid.uuid4()

        # Mock cache miss, then database query
        mock_redis.get.return_value = None
        mock_db.execute.return_value.scalars.return_value.all.return_value = (
            sample_project_goals
        )

        result = await ai_service._get_cached_project_goals(team_id)

        assert len(result) == 2
        assert result[0].description == sample_project_goals[0].description

        # Verify cache was set
        mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_redis_caching_hit(
        self, ai_service, mock_db, mock_redis, sample_project_goals
    ):
        """Test Redis cache hit scenario."""
        team_id = uuid.uuid4()

        # Mock cache hit with serialized goals
        cached_data = [
            {
                "id": str(sample_project_goals[0].id),
                "team_id": str(sample_project_goals[0].team_id),
                "description": sample_project_goals[0].description,
                "priority_weight": sample_project_goals[0].priority_weight,
                "success_metrics": sample_project_goals[0].success_metrics,
                "keywords": ["improve", "user", "experience", "performance"],
            }
        ]
        mock_redis.get.return_value = json.dumps(cached_data, default=str)

        result = await ai_service._get_cached_project_goals(team_id)

        assert len(result) == 1
        assert result[0].description == sample_project_goals[0].description

        # Verify database was not queried
        mock_db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_redis_cache_failure_fallback(
        self, ai_service, mock_db, mock_redis, sample_project_goals
    ):
        """Test fallback to database when Redis fails."""
        team_id = uuid.uuid4()

        # Mock Redis failure
        mock_redis.get.side_effect = Exception("Redis connection failed")
        mock_db.execute.return_value.scalars.return_value.all.return_value = (
            sample_project_goals
        )

        result = await ai_service._get_cached_project_goals(team_id)

        assert len(result) == 2
        assert result[0].description == sample_project_goals[0].description

    def test_calculate_confidence_level(self, ai_service):
        """Test confidence level calculation."""
        # High confidence
        confidence = ai_service._calculate_confidence_level(8.5, 3)
        assert confidence == "high"

        # Medium confidence
        confidence = ai_service._calculate_confidence_level(5.0, 1)
        assert confidence == "medium"

        # Low confidence
        confidence = ai_service._calculate_confidence_level(2.0, 0)
        assert confidence == "low"

    def test_generate_explanation(self, ai_service):
        """Test explanation generation."""
        from app.domains.schemas.ai_prioritization import MatchedGoal

        work_item = MagicMock()
        work_item.title = "Test Item"

        # No matched goals
        explanation = ai_service._generate_explanation(work_item, [], 2.0)
        assert "No strong alignment" in explanation

        # Single matched goal
        matched_goals = [
            MatchedGoal(
                goal_id=uuid.uuid4(),
                goal_title="Improve performance",
                match_strength=5.0,
                matched_keywords=["performance", "optimize"],
            )
        ]
        explanation = ai_service._generate_explanation(work_item, matched_goals, 6.0)
        assert "Improve performance" in explanation
        assert "performance" in explanation

    def test_calculate_clustering_similarity(self, ai_service):
        """Test clustering similarity calculation."""
        work_item_keywords = {"user", "authentication", "security"}
        goal_keywords = {
            uuid.uuid4(): {"user", "experience", "interface"},
            uuid.uuid4(): {"authentication", "security", "login"},
        }

        similarity = ai_service._calculate_clustering_similarity(
            work_item_keywords, goal_keywords
        )

        assert 0.0 <= similarity <= 1.0

        # Test with empty work item keywords
        similarity = ai_service._calculate_clustering_similarity(set(), goal_keywords)
        assert similarity == 0.0

    def test_calculate_business_metrics(self, ai_service):
        """Test business metrics calculation."""
        from app.domains.schemas.ai_prioritization import ScoredWorkItem

        # Empty scored items
        metrics = ai_service._calculate_business_metrics([], [])
        assert metrics.accuracy_score == 0.0
        assert metrics.coverage_percentage == 0.0
        assert metrics.algorithm_version == "1.0.0"

        # Scored items with different confidence levels
        scored_items = [
            ScoredWorkItem(
                work_item_id=uuid.uuid4(),
                title="Item 1",
                current_priority=5.0,
                ai_score=8.0,
                suggested_rank=1,
                confidence_level="high",
                explanation="High confidence explanation",
            ),
            ScoredWorkItem(
                work_item_id=uuid.uuid4(),
                title="Item 2",
                current_priority=3.0,
                ai_score=0.0,
                suggested_rank=2,
                confidence_level="low",
                explanation="Low confidence explanation",
            ),
        ]

        metrics = ai_service._calculate_business_metrics(scored_items, [])

        assert 0.0 <= metrics.accuracy_score <= 1.0
        assert metrics.coverage_percentage == 50.0  # One item with score > 0
        assert metrics.algorithm_version == "1.0.0"

    @pytest.mark.asyncio
    async def test_database_error_handling(self, ai_service, mock_db):
        """Test database error handling."""
        team_id = uuid.uuid4()
        user_id = uuid.uuid4()

        # Mock database error
        mock_db.execute.side_effect = Exception("Database connection failed")

        request = AIPrioritizationRequest(mode="full")

        with pytest.raises(
            DatabaseError, match="An error occurred during AI prioritization scoring"
        ):
            await ai_service.score_work_items(team_id, user_id, request)

    @pytest.mark.asyncio
    async def test_specific_work_item_ids_filtering(
        self, ai_service, mock_db, sample_project_goals, sample_work_items
    ):
        """Test filtering by specific work item IDs."""
        team_id = sample_work_items[0].team_id
        user_id = uuid.uuid4()
        specific_id = sample_work_items[0].id

        # Mock team membership and database queries
        mock_db.execute.side_effect = [
            # Team membership query
            MagicMock(scalar_one_or_none=lambda: MagicMock()),
            # Project goals query
            MagicMock(scalars=lambda: MagicMock(all=lambda: sample_project_goals)),
            # Work items query (filtered)
            MagicMock(scalars=lambda: MagicMock(all=lambda: [sample_work_items[0]])),
        ]

        request = AIPrioritizationRequest(
            work_item_ids=[specific_id], include_metadata=False, mode="full"
        )

        response = await ai_service.score_work_items(team_id, user_id, request)

        assert response.total_items == 1
        assert response.scored_items[0].work_item_id == specific_id

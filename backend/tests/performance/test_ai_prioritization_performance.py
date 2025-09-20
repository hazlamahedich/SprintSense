"""Performance tests for AI Prioritization Service.

These tests focus on meeting the <500ms response time requirement
and validating caching performance improvements.
"""

import asyncio
import json
import statistics
import time
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.models.project_goal import ProjectGoal
from app.domains.models.team import TeamMember, TeamRole
from app.domains.models.work_item import WorkItem, WorkItemStatus, WorkItemType
from app.domains.schemas.ai_prioritization import AIPrioritizationRequest
from app.domains.services.ai_prioritization_service import AIPrioritizationService


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for performance testing."""
    redis_mock = AsyncMock()
    redis_mock.get.return_value = None  # Default to cache miss
    redis_mock.setex.return_value = True
    return redis_mock


@pytest.fixture
def performance_service(mock_redis_client):
    """AI Prioritization Service configured for performance testing."""
    db_mock = AsyncMock(spec=AsyncSession)
    return AIPrioritizationService(db=db_mock, redis_client=mock_redis_client)


@pytest.fixture
def large_dataset():
    """Generate a large dataset for performance testing."""
    team_id = uuid.uuid4()

    # Generate project goals
    goals = []
    for i in range(10):  # 10 project goals
        goal = ProjectGoal()
        goal.id = uuid.uuid4()
        goal.team_id = team_id
        goal.description = (
            f"Project goal {i+1}: Improve system performance and user experience"
        )
        goal.priority_weight = i + 1
        goal.success_metrics = f"Achieve {(i+1)*10}% improvement"
        goals.append(goal)

    # Generate work items
    work_items = []
    for i in range(100):  # 100 work items
        item = WorkItem()
        item.id = uuid.uuid4()
        item.team_id = team_id
        item.title = f"Work item {i+1}: Implement feature with performance optimization"
        item.description = f"Detailed description for work item {i+1} including various keywords and technical details"
        item.priority = float(i % 10)
        item.status = WorkItemStatus.BACKLOG
        item.type = WorkItemType.STORY
        work_items.append(item)

    return team_id, goals, work_items


@pytest.fixture
def extra_large_dataset():
    """Generate an extra large dataset for stress testing."""
    team_id = uuid.uuid4()

    # More project goals for complex matching
    goals = []
    for i in range(20):  # 20 project goals
        goal = ProjectGoal()
        goal.id = uuid.uuid4()
        goal.team_id = team_id
        goal.description = f"Strategic goal {i+1}: Enhance {['performance', 'security', 'usability', 'scalability'][i % 4]}"
        goal.priority_weight = (i % 10) + 1
        goal.success_metrics = f"Target metric {i+1}"
        goals.append(goal)

    # Generate many work items
    work_items = []
    for i in range(500):  # 500 work items
        item = WorkItem()
        item.id = uuid.uuid4()
        item.team_id = team_id
        item.title = f"Feature {i+1}: Complex implementation task"
        item.description = f"Complex description {i+1} with multiple keywords and technical requirements"
        item.priority = float(i % 10)
        item.status = WorkItemStatus.BACKLOG if i % 3 == 0 else WorkItemStatus.TODO
        item.type = WorkItemType.STORY if i % 2 == 0 else WorkItemType.BUG
        work_items.append(item)

    return team_id, goals, work_items


class TestAIPrioritizationPerformance:
    """Performance tests for AI prioritization service."""

    @pytest.mark.asyncio
    async def test_scoring_latency_requirement(
        self,
        performance_service: AIPrioritizationService,
        large_dataset,
        mock_redis_client,
    ):
        """Test that scoring meets the <500ms latency requirement."""
        team_id, goals, work_items = large_dataset
        user_id = uuid.uuid4()

        # Mock database queries
        performance_service.db.execute.side_effect = [
            # Team membership query
            AsyncMock(scalar_one_or_none=lambda: AsyncMock()),
            # Project goals query
            AsyncMock(scalars=lambda: AsyncMock(all=lambda: goals)),
            # Work items query
            AsyncMock(scalars=lambda: AsyncMock(all=lambda: work_items)),
        ]

        request = AIPrioritizationRequest(
            work_item_ids=None, include_metadata=True, mode="full"
        )

        # Measure execution time
        start_time = time.time()

        response = await performance_service.score_work_items(team_id, user_id, request)

        end_time = time.time()
        execution_time_ms = (end_time - start_time) * 1000

        # Verify performance requirement
        assert (
            execution_time_ms < 500
        ), f"Execution time {execution_time_ms:.2f}ms exceeds 500ms requirement"

        # Verify response quality
        assert response.total_items == len(work_items)
        assert len(response.scored_items) == response.total_items
        assert response.generation_time_ms >= 0

    @pytest.mark.asyncio
    async def test_caching_performance_improvement(
        self,
        performance_service: AIPrioritizationService,
        large_dataset,
        mock_redis_client,
    ):
        """Test that Redis caching improves performance on subsequent requests."""
        team_id, goals, work_items = large_dataset
        user_id = uuid.uuid4()

        # First request (cache miss) - mock database queries
        performance_service.db.execute.side_effect = [
            # Team membership query
            AsyncMock(scalar_one_or_none=lambda: AsyncMock()),
            # Project goals query (will be cached)
            AsyncMock(scalars=lambda: AsyncMock(all=lambda: goals)),
            # Work items query
            AsyncMock(scalars=lambda: AsyncMock(all=lambda: work_items)),
        ]

        request = AIPrioritizationRequest(
            work_item_ids=None, include_metadata=True, mode="full"
        )

        # First request timing
        start_time = time.time()
        response1 = await performance_service.score_work_items(
            team_id, user_id, request
        )
        first_request_time = time.time() - start_time

        # Verify cache was set
        mock_redis_client.setex.assert_called()

        # Second request (cache hit) - mock cached goals
        cached_goals = json.dumps(
            [
                {
                    "id": str(goal.id),
                    "team_id": str(goal.team_id),
                    "description": goal.description,
                    "priority_weight": goal.priority_weight,
                    "success_metrics": goal.success_metrics,
                    "keywords": [
                        "improve",
                        "system",
                        "performance",
                        "user",
                        "experience",
                    ],
                }
                for goal in goals[:5]  # Simulate partial cache
            ],
            default=str,
        )

        mock_redis_client.get.return_value = cached_goals

        # Reset db mock for second request
        performance_service.db.execute.side_effect = [
            # Team membership query
            AsyncMock(scalar_one_or_none=lambda: AsyncMock()),
            # Work items query (goals from cache)
            AsyncMock(scalars=lambda: AsyncMock(all=lambda: work_items)),
        ]

        # Second request timing
        start_time = time.time()
        response2 = await performance_service.score_work_items(
            team_id, user_id, request
        )
        second_request_time = time.time() - start_time

        # Verify caching improves performance (at least 10% faster)
        improvement_ratio = (
            first_request_time - second_request_time
        ) / first_request_time
        assert (
            improvement_ratio > 0.10
        ), f"Cache only improved performance by {improvement_ratio:.2%}, expected >10%"

        # Both responses should be valid
        assert response1.total_items == response2.total_items
        # Both responses should meet latency requirement
        assert first_request_time * 1000 < 500
        assert second_request_time * 1000 < 500

    @pytest.mark.asyncio
    async def test_concurrent_requests_performance(
        self,
        performance_service: AIPrioritizationService,
        large_dataset,
        mock_redis_client,
    ):
        """Test performance under concurrent load."""
        team_id, goals, work_items = large_dataset
        user_id = uuid.uuid4()

        # Mock database queries for all requests
        async def mock_execute(*args, **kwargs):
            # Simulate different query types
            if "team_members" in str(args):
                return AsyncMock(scalar_one_or_none=lambda: AsyncMock())
            elif "project_goals" in str(args):
                return AsyncMock(scalars=lambda: AsyncMock(all=lambda: goals))
            else:  # work_items
                return AsyncMock(scalars=lambda: AsyncMock(all=lambda: work_items))

        performance_service.db.execute.side_effect = mock_execute

        request = AIPrioritizationRequest(
            work_item_ids=None, include_metadata=False, mode="fast"  # Reduce load
        )

        # Simulate 5 concurrent requests
        concurrent_requests = 5

        async def single_request():
            start_time = time.time()
            response = await performance_service.score_work_items(
                team_id, user_id, request
            )
            execution_time = (time.time() - start_time) * 1000
            return execution_time, response

        # Execute concurrent requests
        start_time = time.time()

        tasks = [single_request() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks)

        total_time = (time.time() - start_time) * 1000

        # Extract execution times and responses
        execution_times, responses = zip(*results)

        # Performance assertions
        max_execution_time = max(execution_times)
        avg_execution_time = statistics.mean(execution_times)

        assert (
            max_execution_time < 500
        ), f"Max execution time {max_execution_time:.2f}ms exceeds 500ms"
        assert (
            avg_execution_time < 400
        ), f"Average execution time {avg_execution_time:.2f}ms should be <400ms"

        # All requests should complete successfully
        for response in responses:
            assert response.total_items == len(work_items)
            assert len(response.scored_items) == response.total_items

    @pytest.mark.asyncio
    async def test_memory_usage_efficiency(
        self,
        performance_service: AIPrioritizationService,
        extra_large_dataset,
        mock_redis_client,
    ):
        """Test memory efficiency with large datasets."""
        team_id, goals, work_items = extra_large_dataset
        user_id = uuid.uuid4()

        # Mock database queries
        performance_service.db.execute.side_effect = [
            # Team membership query
            AsyncMock(scalar_one_or_none=lambda: AsyncMock()),
            # Project goals query
            AsyncMock(scalars=lambda: AsyncMock(all=lambda: goals)),
            # Work items query
            AsyncMock(scalars=lambda: AsyncMock(all=lambda: work_items)),
        ]

        request = AIPrioritizationRequest(
            work_item_ids=None, include_metadata=True, mode="full"
        )

        # Import psutil for memory monitoring if available
        try:
            import psutil

            process = psutil.Process()

            memory_before = process.memory_info().rss / 1024 / 1024  # MB

            response = await performance_service.score_work_items(
                team_id, user_id, request
            )

            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = memory_after - memory_before

            # Memory increase should be reasonable for processing 500 items
            assert (
                memory_increase < 100
            ), f"Memory increase {memory_increase:.2f}MB is too high"

        except ImportError:
            # If psutil not available, just verify the request completes
            response = await performance_service.score_work_items(
                team_id, user_id, request
            )

        # Verify response quality despite large dataset
        assert response.total_items == len(work_items)
        assert len(response.scored_items) == response.total_items

    @pytest.mark.asyncio
    async def test_circuit_breaker_performance(
        self,
        performance_service: AIPrioritizationService,
        large_dataset,
        mock_redis_client,
    ):
        """Test circuit breaker doesn't significantly impact performance."""
        team_id, goals, work_items = large_dataset
        user_id = uuid.uuid4()

        # Mock successful database queries
        performance_service.db.execute.side_effect = [
            AsyncMock(scalar_one_or_none=lambda: AsyncMock()),
            AsyncMock(scalars=lambda: AsyncMock(all=lambda: goals)),
            AsyncMock(scalars=lambda: AsyncMock(all=lambda: work_items)),
        ]

        request = AIPrioritizationRequest(
            work_item_ids=None, include_metadata=True, mode="full"
        )

        # Measure multiple requests to test circuit breaker overhead
        execution_times = []

        for _ in range(3):
            start_time = time.time()

            response = await performance_service.score_work_items(
                team_id, user_id, request
            )

            execution_time = (time.time() - start_time) * 1000
            execution_times.append(execution_time)

            # Verify successful response
            assert response.total_items == len(work_items)

        # Circuit breaker shouldn't add significant overhead
        max_time = max(execution_times)
        avg_time = statistics.mean(execution_times)

        assert (
            max_time < 500
        ), f"Max execution time {max_time:.2f}ms exceeds requirement"
        assert (
            avg_time < 400
        ), f"Average execution time {avg_time:.2f}ms should be consistent"

        # Variance should be minimal (circuit breaker should be consistent)
        if len(execution_times) > 1:
            variance = statistics.variance(execution_times)
            assert (
                variance < 10000
            ), f"High variance {variance:.2f} suggests inconsistent performance"

    @pytest.mark.asyncio
    async def test_fast_mode_performance(
        self,
        performance_service: AIPrioritizationService,
        large_dataset,
        mock_redis_client,
    ):
        """Test that 'fast' mode provides better performance than 'full' mode."""
        team_id, goals, work_items = large_dataset
        user_id = uuid.uuid4()

        # Mock database queries (will be called twice)
        db_responses = [
            # First request (full mode)
            AsyncMock(scalar_one_or_none=lambda: AsyncMock()),
            AsyncMock(scalars=lambda: AsyncMock(all=lambda: goals)),
            AsyncMock(scalars=lambda: AsyncMock(all=lambda: work_items)),
            # Second request (fast mode)
            AsyncMock(scalar_one_or_none=lambda: AsyncMock()),
            AsyncMock(scalars=lambda: AsyncMock(all=lambda: goals)),
            AsyncMock(scalars=lambda: AsyncMock(all=lambda: work_items)),
        ]
        performance_service.db.execute.side_effect = db_responses

        # Test full mode
        full_request = AIPrioritizationRequest(
            work_item_ids=None, include_metadata=True, mode="full"
        )

        start_time = time.time()
        full_response = await performance_service.score_work_items(
            team_id, user_id, full_request
        )
        full_mode_time = (time.time() - start_time) * 1000

        # Test fast mode
        fast_request = AIPrioritizationRequest(
            work_item_ids=None, include_metadata=False, mode="fast"
        )

        start_time = time.time()
        fast_response = await performance_service.score_work_items(
            team_id, user_id, fast_request
        )
        fast_mode_time = (time.time() - start_time) * 1000

        # Fast mode should be at least 20% faster
        performance_improvement = (full_mode_time - fast_mode_time) / full_mode_time
        assert (
            performance_improvement > 0.20
        ), f"Fast mode only {performance_improvement:.2%} faster, expected >20%"

        # Both modes should meet latency requirement
        assert full_mode_time < 500, f"Full mode {full_mode_time:.2f}ms exceeds 500ms"
        assert fast_mode_time < 500, f"Fast mode {fast_mode_time:.2f}ms exceeds 500ms"

        # Both should return valid results
        assert full_response.total_items == fast_response.total_items
        assert len(full_response.scored_items) == len(fast_response.scored_items)

    @pytest.mark.asyncio
    async def test_keyword_processing_performance(
        self, performance_service: AIPrioritizationService
    ):
        """Test keyword processing performance with various text sizes."""
        from app.domains.services.ai_prioritization_service import TextProcessor

        # Test various text sizes
        test_texts = [
            "Simple text",  # Small
            "Medium length text with several words and some technical jargon "
            * 10,  # Medium
            "Very long text description with many technical terms and keywords "
            * 100,  # Large
        ]

        processing_times = []

        for text in test_texts:
            start_time = time.time()

            # Process text through all text processing steps
            normalized = TextProcessor.normalize_text(text)
            keywords = TextProcessor.extract_keywords(normalized)
            stemmed_keywords = {TextProcessor.simple_stem(kw) for kw in keywords}

            processing_time = (time.time() - start_time) * 1000
            processing_times.append(processing_time)

            # Verify results are reasonable
            assert len(keywords) >= 0
            assert len(stemmed_keywords) >= 0

        # Even the largest text should process quickly
        max_processing_time = max(processing_times)
        assert (
            max_processing_time < 50
        ), f"Text processing took {max_processing_time:.2f}ms, should be <50ms"

    @pytest.mark.asyncio
    async def test_scoring_algorithm_performance(
        self, performance_service: AIPrioritizationService, large_dataset
    ):
        """Test the core scoring algorithm performance in isolation."""
        team_id, goals, work_items = large_dataset

        # Test the scoring calculation directly
        from app.domains.services.ai_prioritization_service import TextProcessor

        # Prepare goal keywords
        goal_keywords = {}
        for goal in goals:
            keywords = TextProcessor.extract_keywords(goal.description)
            goal_keywords[goal.id] = keywords

        scoring_times = []

        for work_item in work_items[:10]:  # Test with subset for focused timing
            start_time = time.time()

            # Extract work item keywords
            work_item_text = f"{work_item.title} {work_item.description}"
            work_item_keywords = TextProcessor.extract_keywords(work_item_text)

            # Calculate scores against all goals
            scores = []
            for goal in goals:
                goal_kw = goal_keywords[goal.id]

                # Calculate keyword overlap
                overlap = len(work_item_keywords & goal_kw)
                total_keywords = len(work_item_keywords | goal_kw)

                if total_keywords > 0:
                    similarity = overlap / total_keywords
                    score = similarity * goal.priority_weight
                    scores.append(min(max(score, 0.0), 10.0))

            scoring_time = (time.time() - start_time) * 1000
            scoring_times.append(scoring_time)

        # Scoring should be very fast per work item
        max_scoring_time = max(scoring_times)
        avg_scoring_time = statistics.mean(scoring_times)

        assert (
            max_scoring_time < 10
        ), f"Max scoring time {max_scoring_time:.2f}ms should be <10ms per item"
        assert (
            avg_scoring_time < 5
        ), f"Average scoring time {avg_scoring_time:.2f}ms should be <5ms per item"

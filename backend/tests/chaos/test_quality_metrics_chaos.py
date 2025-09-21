"""Chaos testing for quality metrics endpoints."""

import asyncio
from unittest.mock import Mock, patch

import numpy as np
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.metrics_logger import metrics_logger
from app.services.recommendations_service import RecommendationsService


@pytest.mark.asyncio
async def test_metrics_under_load(app, async_client: AsyncClient):
    """Test metrics endpoint under heavy load conditions."""
    # Setup
    team_id = "test-team-id"
    num_requests = 50
    concurrent_limit = 10

    async def make_request():
        return await async_client.get(
            f"/teams/{team_id}/recommendations/quality-metrics"
        )

    # Execute requests in batches to simulate realistic load
    responses = []
    for i in range(0, num_requests, concurrent_limit):
        batch = min(concurrent_limit, num_requests - i)
        batch_responses = await asyncio.gather(*[make_request() for _ in range(batch)])
        responses.extend(batch_responses)

    # Verify responses
    success_count = sum(1 for r in responses if r.status_code == 200)
    success_rate = success_count / num_requests

    assert success_rate >= 0.95, f"Success rate {success_rate:.2%} below 95% threshold"

    # Check response times
    response_times = [r.elapsed.total_seconds() for r in responses]
    p95_time = np.percentile(response_times, 95)

    assert (
        p95_time < 0.2
    ), f"95th percentile response time {p95_time:.3f}s exceeds 200ms limit"


@pytest.mark.asyncio
async def test_metrics_with_network_issues(app, async_client: AsyncClient):
    """Test metrics resilience with simulated network issues."""
    team_id = "test-team-id"

    async def flaky_db_call(*args, **kwargs):
        # Simulate random network issues
        if np.random.random() < 0.3:  # 30% failure rate
            await asyncio.sleep(np.random.uniform(0.1, 0.5))
            raise ConnectionError("Simulated network issue")
        return Mock(scalar=lambda: np.random.randint(1, 100))

    with patch(
        "sqlalchemy.ext.asyncio.AsyncSession.execute", side_effect=flaky_db_call
    ):
        responses = await asyncio.gather(
            *[
                async_client.get(f"/teams/{team_id}/recommendations/quality-metrics")
                for _ in range(20)
            ],
            return_exceptions=True,
        )

    # Analyze results
    success_count = sum(
        1 for r in responses if hasattr(r, "status_code") and r.status_code == 200
    )
    error_count = len(responses) - success_count

    # Some requests should succeed despite network issues
    assert success_count > 0, "No requests succeeded under network issues"
    # Some requests should fail due to simulated issues
    assert error_count > 0, "No requests failed despite network issues"


@pytest.mark.asyncio
async def test_metrics_cache_resilience(app, async_client: AsyncClient):
    """Test metrics caching under service degradation."""
    team_id = "test-team-id"

    # First request to populate cache
    initial_response = await async_client.get(
        f"/teams/{team_id}/recommendations/quality-metrics"
    )
    assert initial_response.status_code == 200
    initial_data = initial_response.json()

    # Simulate complete service degradation
    def db_failure(*args, **kwargs):
        raise Exception("Database unavailable")

    with patch("sqlalchemy.ext.asyncio.AsyncSession.execute", side_effect=db_failure):
        # Should still get cached response
        cached_response = await async_client.get(
            f"/teams/{team_id}/recommendations/quality-metrics"
        )
        assert cached_response.status_code == 200
        cached_data = cached_response.json()

        # Verify cache hit
        assert cached_data == initial_data


@pytest.mark.asyncio
async def test_metrics_data_consistency(app, async_client: AsyncClient):
    """Test metrics consistency under concurrent updates."""
    team_id = "test-team-id"

    # Simulate concurrent feedback submissions and metrics requests
    async def concurrent_operations():
        feedback_task = async_client.post(
            f"/work-items/recommendations/test-id/feedback",
            json={"type": "not_useful", "reason": "too_complex"},
        )
        metrics_task = async_client.get(
            f"/teams/{team_id}/recommendations/quality-metrics"
        )

        feedback_resp, metrics_resp = await asyncio.gather(feedback_task, metrics_task)
        return feedback_resp.status_code == 200, metrics_resp.status_code == 200

    results = await asyncio.gather(*[concurrent_operations() for _ in range(10)])

    # Verify all operations completed successfully
    assert all(feedback and metrics for feedback, metrics in results)

    # Final metrics check
    final_metrics = await async_client.get(
        f"/teams/{team_id}/recommendations/quality-metrics"
    )
    assert final_metrics.status_code == 200
    metrics_data = final_metrics.json()

    # Verify metrics are within expected ranges
    assert 0 <= metrics_data["acceptance_rate"] <= 1
    assert metrics_data["feedback_count"] >= 0
    assert all(count >= 0 for count in metrics_data["feedback_reasons"].values())

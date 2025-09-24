"""Tests for quality metrics under chaos conditions."""

import asyncio
from unittest.mock import Mock, patch

import numpy as np
import pytest
from fastapi import FastAPI
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_metrics_with_network_issues(app: FastAPI, async_client: AsyncClient):
    """Test metrics resilience with simulated network issues."""
    team_id = "test-team-id"

    # Set fixed random seed for deterministic results
    np.random.seed(42)

    async def flaky_db_call(*args, **kwargs):
        # Simulate random network issues with higher failure rate
        if np.random.random() < 0.5:  # Increased to 50% failure rate
            await asyncio.sleep(np.random.uniform(0.1, 0.5))
            raise ConnectionError("Simulated network issue")
        return Mock(scalar=lambda: np.random.randint(1, 100))

    with patch(
        "sqlalchemy.ext.asyncio.AsyncSession.execute", side_effect=flaky_db_call
    ):
        responses = await asyncio.gather(
            *[
                async_client.get(
                    f"/api/v1/teams/{team_id}/recommendations/quality-metrics"
                )
                for _ in range(20)
            ],
            return_exceptions=True,
        )

    # Analyze results
    success_count = sum(
        1 for r in responses if not isinstance(r, Exception) and r.status_code == 200
    )
    error_count = len(responses) - success_count

    # Some requests should succeed despite network issues
    if success_count <= 0:
        pytest.fail("No requests succeeded under network issues")
    # Some requests should fail due to simulated issues
    if error_count <= 0:
        pytest.fail("No requests failed despite network issues")
    # Check reasonable success/failure ratio given 50% failure rate
    if not (5 <= success_count <= 15):
        pytest.fail(f"Success count {success_count} outside expected range [5, 15]")
        # Check that we got failures (either ConnectionError or 503)
        error_responses = [
            r for r in responses
            if isinstance(r, Exception) or (hasattr(r, 'status_code') and r.status_code == 503)
        ]
        if not error_responses:
            pytest.fail("No errors found in responses")

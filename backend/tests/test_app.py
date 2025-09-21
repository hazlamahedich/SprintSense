"""Test FastAPI application fixtures."""

from typing import Any, AsyncGenerator, Dict

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from app.api.endpoints import recommendations
from app.core.database import get_db

from .test_database import get_test_db


@pytest.fixture
def app(get_test_db) -> FastAPI:
    """Create test FastAPI application."""
    app = FastAPI()

    # Override the database dependency
    app.dependency_overrides[get_db] = get_test_db

    # Include the recommendations router
    app.include_router(recommendations.router)
    return app


@pytest.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Get async test client."""
    async with AsyncClient(
        app=app,
        base_url="http://test",
        headers={
            "Content-Type": "application/json",
            # Add any default test auth headers here
            "X-Test-User": "test-user",
            "X-Test-Team": "test-team",
        },
    ) as client:
        yield client


@pytest.fixture
def test_metrics_data() -> Dict[str, Any]:
    """Provide test data for quality metrics testing."""
    return {
        "team_id": "test-team-id",
        "metrics": {
            "acceptance_rate": 0.75,
            "recent_acceptance_count": 15,
            "avg_confidence": 0.85,
            "total_recommendations": 100,
            "top_feedback_reason": "too_complex",
            "feedback_count": 25,
            "ui_response_time": 250,
            "backend_response_time_95th": 150,
            "feedback_reasons": {"too_complex": 10, "not_relevant": 8, "duplicate": 7},
        },
    }

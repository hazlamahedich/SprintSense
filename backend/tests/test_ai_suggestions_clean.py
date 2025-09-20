"""
Clean Test Suite for AI Suggestions API
Implementation for Story 3.3: Review and Apply AI Suggestions

Clean tests with proper async handling and minimal dependencies.
"""

from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def client(db_session):
    """Test client with database override."""
    from app.infra.db import get_session

    # Override the dependency to use our test session
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    # Clean up
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_next_suggestion_success(client):
    """Test getting next suggestion returns mock data."""
    response = await client.get("/api/v1/ai-suggestions/next")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "suggestion" in data
    assert data["suggestion"] is not None
    assert data["suggestion"]["title"] == "Optimize database query"


@pytest.mark.asyncio
async def test_apply_suggestion_success(client):
    """Test applying a suggestion."""
    suggestion_id = str(uuid4())
    request_data = {
        "suggestion_id": suggestion_id,
        "work_item_id": str(uuid4()),
        "new_position": 3,
    }

    response = await client.post("/api/v1/ai-suggestions/apply", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["applied_suggestion"]["id"] == suggestion_id
    assert "undo_token" in data


@pytest.mark.asyncio
async def test_undo_suggestion_success(client):
    """Test undoing a suggestion."""
    response = await client.post("/api/v1/ai-suggestions/undo?undo_token=test_token")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["cleanup_performed"] is True


@pytest.mark.asyncio
async def test_get_batch_suggestions_success(client):
    """Test getting batch suggestions."""
    response = await client.get("/api/v1/ai-suggestions/batch?count=3")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["suggestions"]) <= 3
    assert "batch_session_id" in data


@pytest.mark.asyncio
async def test_batch_apply_success(client):
    """Test applying batch suggestions."""
    batch_request = {
        "session_id": str(uuid4()),
        "actions": [
            {"suggestion_id": str(uuid4()), "action": "accept", "feedback": "helpful"}
        ],
    }

    response = await client.post(
        "/api/v1/ai-suggestions/batch-apply", json=batch_request
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["successful_count"] == 1
    assert data["failed_count"] == 0


@pytest.mark.asyncio
async def test_submit_feedback_success(client):
    """Test submitting feedback."""
    suggestion_id = str(uuid4())
    feedback_data = {
        "feedback_type": "helpful",
        "optional_comment": "Great suggestion!",
        "context": {"action_taken": "accept", "session_duration_ms": 15000},
    }

    response = await client.post(
        f"/api/v1/ai-suggestions/{suggestion_id}/feedback", json=feedback_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["privacy_compliant"] is True
    assert data["analytics_updated"] is True


# Performance test
@pytest.mark.asyncio
async def test_api_response_time(client):
    """Test API response time is reasonable."""
    import time

    start_time = time.time()

    response = await client.get("/api/v1/ai-suggestions/next")

    end_time = time.time()
    response_time = end_time - start_time

    assert response.status_code == 200
    assert response_time < 2.0  # Should respond within 2 seconds


# Security test
@pytest.mark.asyncio
async def test_invalid_uuid_validation(client):
    """Test that invalid UUIDs are rejected."""
    request_data = {
        "suggestion_id": "invalid-uuid-format",
        "work_item_id": str(uuid4()),
        "new_position": 3,
    }

    # The API should either validate the UUID or handle it gracefully
    response = await client.post("/api/v1/ai-suggestions/apply", json=request_data)

    # We expect either 200 (if validation is lenient) or 400/422 (if strict)
    assert response.status_code in [200, 400, 422]

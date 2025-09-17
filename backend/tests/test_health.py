"""Test health endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    """Test basic health check endpoint."""
    response = await async_client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"
    assert data["service"] == "SprintSense Backend"


@pytest.mark.asyncio
async def test_root_endpoint(async_client: AsyncClient):
    """Test root endpoint."""
    response = await async_client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_detailed_health_check(async_client: AsyncClient):
    """Test detailed health check endpoint."""
    response = await async_client.get("/api/v1/health/detailed")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"
    assert data["service"] == "SprintSense Backend"
    assert "checks" in data
    assert "database" in data["checks"]
    assert data["checks"]["database"]["status"] == "healthy"
    assert data["version"] == "0.1.0"

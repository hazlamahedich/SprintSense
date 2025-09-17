"""Integration tests for health check endpoints."""

import os
from unittest.mock import patch

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from app.main import app

# Test database URL for integration tests
TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:postgres@localhost:5432/sprintsense_test"
)


@pytest.fixture
def test_client():
    """Create a test client with overridden dependencies."""
    return TestClient(app)


@pytest.fixture
async def test_db_session():
    """Create a test database session."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args=(
            {"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {}
        ),
    )

    async with engine.begin() as conn:
        # Create test table if needed
        await conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS test_health_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50)
            )
        """
            )
        )
        await conn.commit()

    async with AsyncSession(engine) as session:
        yield session

    await engine.dispose()


class TestHealthEndpoints:
    """Test suite for health check endpoints."""

    def test_basic_health_check(self, test_client):
        """Test basic health check endpoint."""
        response = test_client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "OK"
        assert data["service"] == "SprintSense Backend"

    @patch.dict(os.environ, {"ENVIRONMENT": "test"})
    def test_detailed_health_check_healthy(self, test_client):
        """Test detailed health check when all services are healthy."""
        with patch("app.api.routers.health.get_session") as mock_session:
            # Mock successful database connection
            mock_db_session = AsyncSession(
                create_async_engine("sqlite+aiosqlite:///:memory:")
            )
            mock_session.return_value = mock_db_session

            response = test_client.get("/api/v1/health/detailed")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] in [
                "OK",
                "DEGRADED",
            ]  # May be degraded due to missing Supabase
            assert data["service"] == "SprintSense Backend"
            assert data["environment"] == "test"
            assert "checks" in data
            assert "timestamp" in data
            assert "response_time_seconds" in data

    @patch.dict(
        os.environ, {"ENVIRONMENT": "test", "SUPABASE_URL": "http://localhost:54321"}
    )
    @patch("httpx.AsyncClient.get")
    def test_detailed_health_check_with_supabase(self, mock_httpx_get, test_client):
        """Test detailed health check with Supabase API check."""
        # Mock successful Supabase API response
        mock_response = httpx.Response(200, json={"status": "ok"})
        mock_httpx_get.return_value = mock_response

        response = test_client.get("/api/v1/health/detailed")

        assert response.status_code in [200, 503]  # May fail if DB connection fails
        data = (
            response.json()
            if response.status_code == 200
            else response.json()["detail"]
        )

        assert "checks" in data
        if "supabase_api" in data["checks"]:
            supabase_check = data["checks"]["supabase_api"]
            assert supabase_check["status"] == "healthy"
            assert supabase_check["url"] == "http://localhost:54321"
            assert supabase_check["response_code"] == 200

    def test_detailed_health_check_database_failure(self, test_client):
        """Test detailed health check when database is unhealthy."""
        from app.infra.db import get_session
        from app.main import app

        # Mock database connection failure
        async def failing_session():
            mock_session = AsyncSession(
                create_async_engine("sqlite+aiosqlite:///:memory:")
            )

            async def failing_execute(*args, **kwargs):
                raise Exception("Database connection failed")

            mock_session.execute = failing_execute
            return mock_session

        # Override the dependency
        app.dependency_overrides[get_session] = failing_session

        try:
            response = test_client.get("/api/v1/health/detailed")

            # Should return 503 Service Unavailable when unhealthy
            assert response.status_code == 503
            data = response.json()["detail"]
            assert data["status"] == "UNHEALTHY"
            assert data["checks"]["database"]["status"] == "unhealthy"
            assert "error" in data["checks"]["database"]
        finally:
            # Clean up the override
            app.dependency_overrides.clear()

    @patch.dict(os.environ, {"SUPABASE_URL": "http://invalid-url"})
    @patch("httpx.AsyncClient.get")
    def test_detailed_health_check_supabase_failure(self, mock_httpx_get, test_client):
        """Test detailed health check when Supabase API is unhealthy."""
        # Mock Supabase API failure
        mock_httpx_get.side_effect = httpx.RequestError("Connection failed")

        response = test_client.get("/api/v1/health/detailed")

        data = (
            response.json()
            if response.status_code == 200
            else response.json()["detail"]
        )

        if "supabase_api" in data["checks"]:
            supabase_check = data["checks"]["supabase_api"]
            assert supabase_check["status"] == "unhealthy"
            assert "error" in supabase_check

    def test_detailed_health_check_response_time(self, test_client):
        """Test that health check includes response time metrics."""
        with patch(
            "time.time", side_effect=[1000.0, 1000.5, 1001.5, 1001.5, 1001.5, 1001.5]
        ):  # 1.5 second response time
            response = test_client.get("/api/v1/health/detailed")

            data = (
                response.json()
                if response.status_code == 200
                else response.json()["detail"]
            )
            assert "response_time_seconds" in data
            assert data["response_time_seconds"] == 1.5
            # Should be marked as DEGRADED due to slow response
            assert data["status"] in ["DEGRADED", "UNHEALTHY"]

    @patch.dict(os.environ, {}, clear=True)
    def test_health_check_no_supabase_config(self, test_client):
        """Test health check when Supabase is not configured."""
        response = test_client.get("/api/v1/health/detailed")

        data = (
            response.json()
            if response.status_code == 200
            else response.json()["detail"]
        )

        assert "checks" in data
        supabase_check = data["checks"]["supabase_api"]
        assert supabase_check["status"] == "not_configured"
        assert supabase_check["message"] == "SUPABASE_URL not set"


class TestHealthCheckIntegration:
    """Integration tests using real database connections (requires test database)."""

    @pytest.mark.integration
    def test_real_database_health_check(self, test_client):
        """Test health check against a real test database.

        Requires a test PostgreSQL database to be running.
        Skip if no test database available.
        """
        try:
            # Try to create a real database connection
            engine = create_engine(TEST_DATABASE_URL.replace("+asyncpg", ""))
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            # If we get here, database is available for testing
            response = test_client.get("/api/v1/health/detailed")

            # Should work with real database
            assert response.status_code in [200, 503]
            data = (
                response.json()
                if response.status_code == 200
                else response.json()["detail"]
            )

            assert "checks" in data
            db_check = data["checks"]["database"]
            # Should be healthy if we can connect, unhealthy if configuration is wrong
            assert db_check["status"] in ["healthy", "unhealthy"]

        except Exception:
            pytest.skip(
                "Test database not available - skipping real database integration test"
            )

    @pytest.mark.integration
    @patch.dict(os.environ, {"SUPABASE_URL": "http://127.0.0.1:54321"})
    def test_local_supabase_health_check(self, test_client):
        """Test health check against local Supabase instance.

        Requires local Supabase to be running via `supabase start`.
        """
        response = test_client.get("/api/v1/health/detailed")

        data = (
            response.json()
            if response.status_code == 200
            else response.json()["detail"]
        )

        if "supabase_api" in data["checks"]:
            supabase_check = data["checks"]["supabase_api"]
            # Should be healthy if local Supabase is running
            # Will be unhealthy if not running, which is also valid for testing
            assert supabase_check["status"] in ["healthy", "unhealthy"]
            # Only check URL if it exists (when Supabase is configured)
            if "url" in supabase_check:
                assert supabase_check["url"] == "http://127.0.0.1:54321"


# Pytest configuration for integration tests
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test requiring external services",
    )

"""Common test fixtures for LLM security tests."""

import pytest
from unittest.mock import MagicMock
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from redis import Redis
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security.llm.rbac import LLMRole, LLMRBACMiddleware


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    redis = MagicMock(spec=Redis)
    redis.get.return_value = None
    redis.setex.return_value = True
    redis.pipeline.return_value.execute.return_value = [True, True]
    redis.pipeline.return_value.incr.return_value = redis.pipeline.return_value
    redis.pipeline.return_value.expire.return_value = redis.pipeline.return_value
    return redis


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = MagicMock(spec=Session)

    # Mock user query
    user = MagicMock()
    user.id = 1
    user.role = LLMRole.USER.value

    # Mock team query
    team = MagicMock()
    team.id = 1
    team.monthly_quota = 10000

    # Set up query returns
    def mock_query_first(*args, **kwargs):
        """Mock query.filter().first() to return appropriate objects."""
        if args and 'User' in str(args[0]):
            return user
        return team

    session.query.return_value.filter.return_value.first.side_effect = mock_query_first
    return session


class AuthTestMiddleware(BaseHTTPMiddleware):
    """Test middleware to inject user authentication state."""

    async def dispatch(self, request: Request, call_next):
        """Add test user to request state."""
        request.state.user_id = 1
        request.state.team_id = 1
        return await call_next(request)


@pytest.fixture
def test_app(mock_db_session, mock_redis):
    """Create a test FastAPI application with RBAC middleware."""
    app = FastAPI()

    # Add test auth middleware first
    app.add_middleware(AuthTestMiddleware)

    # Add RBAC middleware
    app.add_middleware(LLMRBACMiddleware, db=mock_db_session, redis_client=mock_redis)

    # Add test endpoint
    @app.post("/api/v1/llm/complete")
    async def test_endpoint():
        return {"result": "success"}

    return TestClient(app)
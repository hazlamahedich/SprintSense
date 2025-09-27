"""Tests for LLM RBAC system."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security.llm.rbac import (
    Base,
    LLMRBACManager,
    LLMRBACMiddleware,
    LLMRole,
    Team,
    User
)

# Create in-memory database for testing
engine = create_engine(
    'sqlite:///:memory:',
    connect_args={'check_same_thread': False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    redis = MagicMock(spec=Redis)
    redis.get.return_value = b"0"
    redis.pipeline.return_value.execute.return_value = [True, True]
    return redis

@pytest.fixture
def rbac_manager(db, mock_redis):
    """Create an RBAC manager instance."""
    return LLMRBACManager(db, mock_redis)

@pytest.fixture
def test_app(db, mock_redis):
    """Create a test FastAPI application with RBAC middleware."""
    app = FastAPI()
    app.add_middleware(LLMRBACMiddleware, db=db, redis_client=mock_redis)

    @app.post("/api/v1/llm/complete")
    async def protected_endpoint():
        return {"status": "success"}

    return TestClient(app)

def create_test_user(db: Session, role: LLMRole = LLMRole.USER) -> User:
    """Create a test user.

    Args:
        db: Database session
        role: User role

    Returns:
        Created user
    """
    user = User(email=f"test_{role}@example.com", role=role.value)
    db.add(user)
    db.commit()
    return user

def create_test_team(db: Session, name: str = "test_team") -> Team:
    """Create a test team.

    Args:
        db: Database session
        name: Team name

    Returns:
        Created team
    """
    team = Team(name=name, monthly_quota=10000)
    db.add(team)
    db.commit()
    return team

class TestLLMRBACManager:
    """Test the RBAC manager functionality."""

    def test_get_user_permissions_admin(self, rbac_manager, db):
        """Test getting admin user permissions."""
        user = create_test_user(db, LLMRole.ADMIN)
        perms = rbac_manager.get_user_permissions(user.id)

        assert perms.can_create is True
        assert perms.can_manage_teams is True
        assert perms.can_delete is True

    def test_get_user_permissions_regular_user(self, rbac_manager, db):
        """Test getting regular user permissions."""
        user = create_test_user(db, LLMRole.USER)
        perms = rbac_manager.get_user_permissions(user.id)

        assert perms.can_create is True
        assert perms.can_manage_teams is False
        assert perms.can_delete is False

    def test_get_user_permissions_read_only(self, rbac_manager, db):
        """Test getting read-only user permissions."""
        user = create_test_user(db, LLMRole.READ_ONLY)
        perms = rbac_manager.get_user_permissions(user.id)

        assert perms.can_create is False
        assert perms.can_manage_teams is False
        assert perms.can_delete is False

    def test_get_user_permissions_not_found(self, rbac_manager):
        """Test error when user not found."""
        with pytest.raises(HTTPException) as exc:
            rbac_manager.get_user_permissions(999)
        assert exc.value.status_code == 404

    def test_check_permission_granted(self, rbac_manager, db):
        """Test permission check when granted."""
        user = create_test_user(db, LLMRole.ADMIN)
        assert rbac_manager.check_permission(user.id, "can_create") is True

    def test_check_permission_denied(self, rbac_manager, db):
        """Test permission check when denied."""
        user = create_test_user(db, LLMRole.READ_ONLY)
        assert rbac_manager.check_permission(user.id, "can_create") is False

    def test_get_user_teams(self, rbac_manager, db):
        """Test getting user's teams."""
        user = create_test_user(db)
        team = create_test_team(db)

        user.teams.append(team)
        db.commit()

        teams = rbac_manager.get_user_teams(user.id)
        assert len(teams) == 1
        assert teams[0].name == "test_team"

    @pytest.mark.asyncio
    async def test_check_quota_within_limits(self, rbac_manager, db, mock_redis):
        """Test quota check within limits."""
        user = create_test_user(db)
        team = create_test_team(db)
        mock_redis.get.return_value = b"100"  # Current usage

        assert await rbac_manager.check_quota(user.id, team.id, 50) is True

    @pytest.mark.asyncio
    async def test_check_quota_exceeded(self, rbac_manager, db, mock_redis):
        """Test quota check when exceeded."""
        user = create_test_user(db)
        team = create_test_team(db)
        mock_redis.get.return_value = b"9900"  # Near quota limit

        with pytest.raises(HTTPException) as exc:
            await rbac_manager.check_quota(user.id, team.id, 200)
        assert exc.value.status_code == 429
        assert "quota exceeded" in exc.value.detail

    @pytest.mark.asyncio
    async def test_check_quota_rate_limit(self, rbac_manager, db, mock_redis):
        """Test rate limiting."""
        user = create_test_user(db)
        team = create_test_team(db)
        mock_redis.get.side_effect = [b"1000", b"0"]  # Rate limit exceeded

        with pytest.raises(HTTPException) as exc:
            await rbac_manager.check_quota(user.id, team.id, 50)
        assert exc.value.status_code == 429
        assert "Rate limit exceeded" in exc.value.detail

    @pytest.mark.asyncio
    async def test_track_usage(self, rbac_manager, mock_redis):
        """Test usage tracking."""
        await rbac_manager.track_usage(1, 1, 100)
        mock_redis.incr.assert_called_once()

class TestLLMRBACMiddleware:
    """Test the RBAC middleware functionality."""

    def test_middleware_requires_auth(self, test_app):
        """Test that middleware requires authentication."""
        response = test_app.post("/api/v1/llm/complete")
        assert response.status_code == 401

    def test_middleware_checks_permissions(self, test_app, db):
        """Test that middleware checks permissions."""
        user = create_test_user(db, LLMRole.READ_ONLY)
        team = create_test_team(db)

        response = test_app.post(
            "/api/v1/llm/complete",
            headers={"X-User-ID": str(user.id)},
            json={"tokens": 50}
        )
        assert response.status_code == 403

    def test_middleware_allows_access(self, test_app, db):
        """Test that middleware allows valid access."""
        user = create_test_user(db, LLMRole.USER)
        team = create_test_team(db)
        user.teams.append(team)
        db.commit()

        response = test_app.post(
            "/api/v1/llm/complete",
            headers={
                "X-User-ID": str(user.id),
                "X-Team-ID": str(team.id)
            },
            json={"tokens": 50}
        )
        assert response.status_code == 200

    def test_middleware_tracks_usage(self, test_app, db, mock_redis):
        """Test that middleware tracks usage."""
        user = create_test_user(db, LLMRole.USER)
        team = create_test_team(db)
        user.teams.append(team)
        db.commit()

        response = test_app.post(
            "/api/v1/llm/complete",
            headers={
                "X-User-ID": str(user.id),
                "X-Team-ID": str(team.id)
            },
            json={"tokens": 50}
        )

        assert response.status_code == 200
        mock_redis.incr.assert_called()
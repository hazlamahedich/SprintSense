"""Tests for project goals API endpoints."""

import pytest
import pytest_asyncio
from datetime import timedelta
from httpx import AsyncClient
from unittest.mock import patch
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import contextmanager

from app.core.config import settings
from app.core.security import create_access_token
from app.domains.models.project_goal import ProjectGoal
from app.domains.models.team import Team, TeamMember, TeamRole
from app.domains.models.user import User

async def make_auth_request(async_client: AsyncClient, method: str, url: str, user: User, **kwargs):
    """Helper to make authenticated requests."""
    auth_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=timedelta(minutes=30),
    )
    return await async_client.request(
        method=method,
        url=f"{settings.API_V1_STR}{url}",
        cookies={"access_token": auth_token},
        **kwargs
    )
from app.core.security import create_access_token
from app.domains.models.project_goal import ProjectGoal
from app.domains.models.team import Team, TeamMember, TeamRole
from app.domains.models.user import User


class TestProjectGoalsAPI:
    """Test project goals API endpoints."""

    @pytest_asyncio.fixture
    async def sample_team(self, db_session: AsyncSession) -> Team:
        """Create a sample team for testing."""
        team = Team(
            name="Test Team"
        )
        db_session.add(team)
        await db_session.flush()
        return team

    @pytest_asyncio.fixture
    async def sample_owner(self, db_session: AsyncSession) -> User:
        """Create a sample team owner for testing."""
        user = User(
            email="owner@example.com",
            full_name="Team Owner",
            hashed_password="hashed_pw",
            is_active=True,
        )
        db_session.add(user)
        await db_session.flush()
        return user

    @pytest_asyncio.fixture
    async def sample_member(self, db_session: AsyncSession) -> User:
        """Create a sample team member for testing."""
        user = User(
            email="member@example.com",
            full_name="Team Member",
            hashed_password="hashed_pw",
            is_active=True,
        )
        db_session.add(user)
        await db_session.flush()
        return user

    @pytest_asyncio.fixture
    async def team_with_owner(
        self, db_session: AsyncSession, sample_team: Team, sample_owner: User
    ) -> tuple[Team, User]:
        """Create team membership for owner."""
        team = sample_team
        owner = sample_owner

        membership = TeamMember(
            team_id=team.id,
            user_id=owner.id,
            role=TeamRole.OWNER,
        )
        db_session.add(membership)
        await db_session.commit()
        await db_session.refresh(membership)
        await db_session.refresh(team)
        await db_session.refresh(owner)
        return team, owner

    @pytest_asyncio.fixture
    async def team_with_member(
        self, db_session: AsyncSession, sample_team: Team, sample_member: User
    ) -> tuple[Team, User]:
        """Create team membership for regular member."""
        team = sample_team
        member = sample_member

        membership = TeamMember(
            team_id=team.id,
            user_id=member.id,
            role=TeamRole.MEMBER,
        )
        db_session.add(membership)
        await db_session.commit()
        await db_session.refresh(membership)
        await db_session.refresh(team)
        await db_session.refresh(member)
        return team, member

    @pytest.mark.asyncio
    async def test_get_empty_goals_list(
        self,
        async_client: AsyncClient,
        team_with_owner: tuple[Team, User],
    ):
        """Test getting empty goals list returns correct structure."""
        team, owner = team_with_owner

        # Generate auth token for owner
        auth_token = create_access_token(
            data={"sub": str(owner.id), "email": owner.email},
            expires_delta=timedelta(minutes=30),
        )

        response = await async_client.get(
            f"{settings.API_V1_STR}/teams/{team.id}/goals",
            cookies={"access_token": auth_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert data == {"goals": [], "total": 0}

    @pytest.mark.asyncio
    async def test_create_goal_as_owner_success(
        self,
        async_client: AsyncClient,
        team_with_owner: tuple[Team, User],
    ):
        """Test creating goal as team owner succeeds."""
        team, owner = team_with_owner

        goal_data = {
            "description": "Improve user engagement by 25%",
            "priority_weight": 8,
            "success_metrics": "Increase MAU by 25%",
        }

        auth_token = create_access_token(
            data={"sub": str(owner.id), "email": owner.email},
            expires_delta=timedelta(minutes=30),
        )

        response = await async_client.post(
            f"{settings.API_V1_STR}/teams/{team.id}/goals",
            json=goal_data,
            cookies={"access_token": auth_token},
        )

        assert response.status_code == 201
        data = response.json()

        assert data["description"] == goal_data["description"]
        assert data["priority_weight"] == goal_data["priority_weight"]
        assert data["success_metrics"] == goal_data["success_metrics"]
        assert data["team_id"] == str(team.id)
        assert data["author_id"] == str(owner.id)
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_goal_as_member_forbidden(
        self,
        async_client: AsyncClient,
        team_with_member: tuple[Team, User],
    ):
        """Test creating goal as team member is forbidden."""
        team, member = team_with_member

        goal_data = {
            "description": "Improve user engagement by 25%",
            "priority_weight": 8,
        }

        auth_token = create_access_token(
            data={"sub": str(member.id), "email": member.email},
            expires_delta=timedelta(minutes=30),
        )

        response = await async_client.post(
            f"{settings.API_V1_STR}/teams/{team.id}/goals",
            json=goal_data,
            cookies={"access_token": auth_token},
        )

        assert response.status_code == 403
        data = response.json()
        err = data if "code" in data else data.get("error", data.get("detail", {}))
        assert err.get("code") == "INSUFFICIENT_PERMISSIONS"

    @pytest.mark.asyncio
    async def test_get_goals_as_member_allowed(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        team_with_member: tuple[Team, User],
        sample_owner: User,
    ):
        """Test getting goals as team member is allowed."""
        team, member = team_with_member
        owner = sample_owner

        # Add owner to team and create a goal
        owner_membership = TeamMember(
            team_id=team.id,
            user_id=owner.id,
            role=TeamRole.OWNER,
        )
        db_session.add(owner_membership)
        await db_session.flush()

        goal = ProjectGoal(
            team_id=team.id,
            description="Test goal",
            priority_weight=5,
            author_id=sample_owner.id,
            created_by=sample_owner.id,
        )
        db_session.add(goal)
        await db_session.commit()
        await db_session.refresh(owner_membership)
        await db_session.refresh(team)
        await db_session.refresh(goal)

        # Member should be able to view goals
        auth_token = create_access_token(
            data={"sub": str(member.id), "email": member.email},
            expires_delta=timedelta(minutes=30),
        )

        response = await async_client.get(
            f"{settings.API_V1_STR}/teams/{team.id}/goals",
            cookies={"access_token": auth_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["goals"]) == 1
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_goal_description_validation(
        self,
        async_client: AsyncClient,
        team_with_owner: tuple[Team, User],
    ):
        """Test goal description validation."""
        team, owner = team_with_owner

        # Test empty description
        goal_data = {
            "description": "",
            "priority_weight": 5,
        }

        auth_token = create_access_token(
            data={"sub": str(owner.id), "email": owner.email},
            expires_delta=timedelta(minutes=30),
        )

        response = await async_client.post(
            f"{settings.API_V1_STR}/teams/{team.id}/goals",
            json=goal_data,
            cookies={"access_token": auth_token},
        )

        assert response.status_code == 422

        # Test description too long (over 500 chars)
        goal_data = {
            "description": "x" * 501,
            "priority_weight": 5,
        }

        response = await make_auth_request(
            async_client,
            "POST",
            f"/teams/{team.id}/goals",
            owner,
            json=goal_data
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_priority_weight_validation(
        self,
        async_client: AsyncClient,
        team_with_owner: tuple[Team, User],
    ):
        """Test priority weight validation."""
        team, owner = team_with_owner

        # Test priority weight too low
        goal_data = {
            "description": "Valid description",
            "priority_weight": 0,
        }

        response = await make_auth_request(
            async_client,
            "POST",
            f"/teams/{team.id}/goals",
            owner,
            json=goal_data
        )

        assert response.status_code == 422

        # Test priority weight too high
        goal_data = {
            "description": "Valid description",
            "priority_weight": 11,
        }

        response = await make_auth_request(
            async_client,
            "POST",
            f"/teams/{team.id}/goals",
            owner,
            json=goal_data
        )

        assert response.status_code == 422

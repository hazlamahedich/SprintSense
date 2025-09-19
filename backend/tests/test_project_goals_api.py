"""Basic tests for project goal API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.models.project_goal import ProjectGoal
from app.domains.models.team import Team, TeamMember, TeamRole
from app.domains.models.user import User


class TestProjectGoalsAPI:
    """Test project goals API endpoints."""

    @pytest.fixture
    async def sample_team(self, db_session: AsyncSession) -> Team:
        """Create a sample team for testing."""
        team = Team(name="Test Team")
        db_session.add(team)
        await db_session.commit()
        await db_session.refresh(team)
        return team

    @pytest.fixture
    async def sample_owner(self, db_session: AsyncSession) -> User:
        """Create a sample team owner for testing."""
        user = User(
            email="owner@example.com",
            username="teamowner",
            hashed_password="hashed_pw",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.fixture
    async def sample_member(self, db_session: AsyncSession) -> User:
        """Create a sample team member for testing."""
        user = User(
            email="member@example.com",
            username="teammember",
            hashed_password="hashed_pw",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.fixture
    async def team_with_owner(
        self, db_session: AsyncSession, sample_team: Team, sample_owner: User
    ) -> tuple[Team, User]:
        """Create team membership for owner."""
        membership = TeamMember(
            team_id=sample_team.id,
            user_id=sample_owner.id,
            role=TeamRole.OWNER,
        )
        db_session.add(membership)
        await db_session.commit()
        return sample_team, sample_owner

    @pytest.fixture
    async def team_with_member(
        self, db_session: AsyncSession, sample_team: Team, sample_member: User
    ) -> tuple[Team, User]:
        """Create team membership for regular member."""
        membership = TeamMember(
            team_id=sample_team.id,
            user_id=sample_member.id,
            role=TeamRole.MEMBER,
        )
        db_session.add(membership)
        await db_session.commit()
        return sample_team, sample_member

    async def test_get_empty_goals_list(
        self,
        client: AsyncClient,
        team_with_owner: tuple[Team, User],
    ):
        """Test getting empty goals list returns correct structure."""
        team, owner = team_with_owner

        # Mock authentication to return the owner
        with patch_auth(owner):
            response = await client.get(f"/teams/{team.id}/goals")

        assert response.status_code == 200
        data = response.json()
        assert data == {"goals": [], "total": 0}

    async def test_create_goal_as_owner_success(
        self,
        client: AsyncClient,
        team_with_owner: tuple[Team, User],
    ):
        """Test creating goal as team owner succeeds."""
        team, owner = team_with_owner

        goal_data = {
            "description": "Improve user engagement by 25%",
            "priority_weight": 8,
            "success_metrics": "Increase MAU by 25%",
        }

        with patch_auth(owner):
            response = await client.post(f"/teams/{team.id}/goals", json=goal_data)

        assert response.status_code == 201
        data = response.json()

        assert data["description"] == goal_data["description"]
        assert data["priority_weight"] == goal_data["priority_weight"]
        assert data["success_metrics"] == goal_data["success_metrics"]
        assert data["team_id"] == str(team.id)
        assert data["author_id"] == str(owner.id)
        assert "id" in data
        assert "created_at" in data

    async def test_create_goal_as_member_forbidden(
        self,
        client: AsyncClient,
        team_with_member: tuple[Team, User],
    ):
        """Test creating goal as team member is forbidden."""
        team, member = team_with_member

        goal_data = {
            "description": "Improve user engagement by 25%",
            "priority_weight": 8,
        }

        with patch_auth(member):
            response = await client.post(f"/teams/{team.id}/goals", json=goal_data)

        assert response.status_code == 403
        data = response.json()
        assert data["code"] == "INSUFFICIENT_PERMISSIONS"

    async def test_get_goals_as_member_allowed(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        team_with_member: tuple[Team, User],
        sample_owner: User,
    ):
        """Test getting goals as team member is allowed."""
        team, member = team_with_member

        # Add owner to team and create a goal
        owner_membership = TeamMember(
            team_id=team.id,
            user_id=sample_owner.id,
            role=TeamRole.OWNER,
        )
        db_session.add(owner_membership)

        goal = ProjectGoal(
            team_id=team.id,
            description="Test goal",
            priority_weight=5,
            author_id=sample_owner.id,
            created_by=sample_owner.id,
        )
        db_session.add(goal)
        await db_session.commit()

        # Member should be able to view goals
        with patch_auth(member):
            response = await client.get(f"/teams/{team.id}/goals")

        assert response.status_code == 200
        data = response.json()
        assert len(data["goals"]) == 1
        assert data["total"] == 1

    async def test_goal_description_validation(
        self,
        client: AsyncClient,
        team_with_owner: tuple[Team, User],
    ):
        """Test goal description validation."""
        team, owner = team_with_owner

        # Test empty description
        goal_data = {
            "description": "",
            "priority_weight": 5,
        }

        with patch_auth(owner):
            response = await client.post(f"/teams/{team.id}/goals", json=goal_data)

        assert response.status_code == 422

        # Test description too long (over 500 chars)
        goal_data = {
            "description": "x" * 501,
            "priority_weight": 5,
        }

        with patch_auth(owner):
            response = await client.post(f"/teams/{team.id}/goals", json=goal_data)

        assert response.status_code == 422

    async def test_priority_weight_validation(
        self,
        client: AsyncClient,
        team_with_owner: tuple[Team, User],
    ):
        """Test priority weight validation."""
        team, owner = team_with_owner

        # Test priority weight too low
        goal_data = {
            "description": "Valid description",
            "priority_weight": 0,
        }

        with patch_auth(owner):
            response = await client.post(f"/teams/{team.id}/goals", json=goal_data)

        assert response.status_code == 422

        # Test priority weight too high
        goal_data = {
            "description": "Valid description",
            "priority_weight": 11,
        }

        with patch_auth(owner):
            response = await client.post(f"/teams/{team.id}/goals", json=goal_data)

        assert response.status_code == 422


# Helper function for mocking authentication
def patch_auth(user: User):
    """Mock authentication to return specific user."""
    from unittest.mock import patch

    async def mock_get_current_user():
        return user

    return patch("app.core.auth.get_current_user", side_effect=mock_get_current_user)

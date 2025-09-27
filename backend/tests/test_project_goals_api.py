"""Basic tests for project goal API endpoints."""

from contextlib import contextmanager
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.domains.models.project_goal import ProjectGoal
from app.domains.models.team import Team, TeamMember, TeamRole
from app.domains.models.user import User


@pytest.mark.asyncio
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
        import uuid

        user = User(
            email=f"owner_{uuid.uuid4()}@example.com",  # Unique email
            full_name="Team Owner",
            hashed_password="hashed_pw",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.fixture
    async def sample_member(self, db_session: AsyncSession) -> User:
        """Create a sample team member for testing."""
        import uuid

        user = User(
            email=f"member_{uuid.uuid4()}@example.com",  # Unique email
            full_name="Team Member",
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
        # Await the sample fixtures first
        team = await sample_team
        owner = await sample_owner

        membership = TeamMember(
            team_id=team.id,
            user_id=owner.id,
            role=TeamRole.OWNER,
        )
        db_session.add(membership)
        await db_session.commit()
        return team, owner

    @pytest.fixture
    async def team_with_member(
        self, db_session: AsyncSession, sample_team: Team, sample_member: User
    ) -> tuple[Team, User]:
        """Create team membership for regular member."""
        # Await the sample fixtures first
        team = await sample_team
        member = await sample_member

        membership = TeamMember(
            team_id=team.id,
            user_id=member.id,
            role=TeamRole.MEMBER,
        )
        db_session.add(membership)
        await db_session.commit()
        return team, member

    @contextmanager
    def patch_auth(self, user: User):
        from app.core.auth import get_current_user

        app_module = "app"
        with patch(f"{app_module}.core.auth.get_current_user") as mock_auth:
            mock_auth.return_value = user
            yield

    async def test_get_empty_goals_list(
        self, client: AsyncClient, team_with_owner: tuple[Team, User], app
    ):
        """Test getting empty goals list returns correct structure."""
        team, owner = await team_with_owner

        # Mock authentication
        async def mock_auth():
            return owner

        app.dependency_overrides[get_current_user] = mock_auth
        headers = {"Authorization": f"Bearer {owner.id}"}

        response = await client.get(f"/api/v1/teams/{team.id}/goals", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data == {"goals": [], "total": 0}

    async def test_create_goal_as_owner_success(
        self,
        client: AsyncClient,
        team_with_owner: tuple[Team, User],
    ):
        """Test creating goal as team owner succeeds."""
        team, owner = await team_with_owner

        goal_data = {
            "description": "Improve user engagement by 25%",
            "priority_weight": 8,
            "success_metrics": "Increase MAU by 25%",
        }

        from datetime import timedelta

        from app.core.security import create_access_token

        token = create_access_token(
            subject=str(owner.id),
            expires_delta=timedelta(minutes=30),
            email=owner.email
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post(
            f"/api/v1/teams/{team.id}/goals", json=goal_data, headers=headers
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

    async def test_create_goal_as_member_forbidden(
        self,
        client: AsyncClient,
        team_with_member: tuple[Team, User],
    ):
        """Test creating goal as team member is forbidden."""
        team, member = await team_with_member

        goal_data = {
            "description": "Improve user engagement by 25%",
            "priority_weight": 8,
        }

        from datetime import timedelta

        from app.core.security import create_access_token

        token = create_access_token(
            subject=str(member.id),
            expires_delta=timedelta(minutes=30),
            email=member.email
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post(
            f"/api/v1/teams/{team.id}/goals", json=goal_data, headers=headers
        )

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
        team, member = await team_with_member
        owner = await sample_owner

        # Add owner to team and create a goal
        owner_membership = TeamMember(
            team_id=team.id,
            user_id=owner.id,
            role=TeamRole.OWNER,
        )
        db_session.add(owner_membership)

        goal = ProjectGoal(
            team_id=team.id,
            description="Test goal",
            priority_weight=5,
            author_id=owner.id,
            created_by=owner.id,
        )
        db_session.add(goal)
        await db_session.commit()

        # Member should be able to view goals
        from datetime import timedelta

        from app.core.security import create_access_token

        token = create_access_token(
            data={"sub": str(member.id), "email": member.email},
            expires_delta=timedelta(minutes=30),
        )
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get(f"/api/v1/teams/{team.id}/goals", headers=headers)

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
        team, owner = await team_with_owner

        # Test empty description
        goal_data = {
            "description": "",
            "priority_weight": 5,
        }

        from datetime import timedelta

        from app.core.security import create_access_token

        token = create_access_token(
            subject=str(owner.id),
            expires_delta=timedelta(minutes=30),
            email=owner.email
        )
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            f"/api/v1/teams/{team.id}/goals", json=goal_data, headers=headers
        )

        assert response.status_code == 422

        # Test description too long (over 500 chars)
        goal_data = {
            "description": "x" * 501,
            "priority_weight": 5,
        }

        from datetime import timedelta

        from app.core.security import create_access_token

        token = create_access_token(
            subject=str(owner.id),
            expires_delta=timedelta(minutes=30),
            email=owner.email
        )
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            f"/api/v1/teams/{team.id}/goals", json=goal_data, headers=headers
        )

        assert response.status_code == 422

    async def test_priority_weight_validation(
        self, client: AsyncClient, team_with_owner: tuple[Team, User], app
    ):
        """Test priority weight validation."""
        team, owner = await team_with_owner

        # Test priority weight too low
        goal_data = {
            "description": "Valid description",
            "priority_weight": 0,
        }

        # Mock authentication
        async def mock_auth():
            return owner

        app.dependency_overrides[get_current_user] = mock_auth
        headers = {"Authorization": f"Bearer {owner.id}"}

        response = await client.post(
            f"/api/v1/teams/{team.id}/goals", json=goal_data, headers=headers
        )

        assert response.status_code == 422

        # Test priority weight too high
        goal_data = {
            "description": "Valid description",
            "priority_weight": 11,
        }

        with self.patch_auth(owner):
            response = await client.post(
                f"/api/v1/teams/{team.id}/goals", json=goal_data
            )

        assert response.status_code == 422

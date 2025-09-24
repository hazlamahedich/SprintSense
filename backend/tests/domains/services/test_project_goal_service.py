"""Unit tests for ProjectGoalService."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError, ValidationError
from app.domains.models.project_goal import ProjectGoal
from app.domains.models.team import Team, TeamMember, TeamRole
from app.domains.models.user import User
from app.domains.schemas.project_goal import (
    ProjectGoalCreateRequest,
    ProjectGoalUpdateRequest,
)


class TestProjectGoalService:
    """Tests for project goal service operations."""

    @pytest_asyncio.fixture
    async def test_team(self, db_session: AsyncSession) -> Team:
        """Create a test team."""
        team = Team(name="Test Team")
        db_session.add(team)
        await db_session.flush()
        return team

    @pytest_asyncio.fixture
    async def team_owner(self, db_session: AsyncSession) -> User:
        """Create a test owner user."""
        user = User(
            email="owner@example.com",
            full_name="Team Owner",
            hashed_password="hashed_password",
            is_active=True,
        )
        db_session.add(user)
        await db_session.flush()
        return user

    @pytest_asyncio.fixture
    async def team_member(self, db_session: AsyncSession) -> User:
        """Create a test member user."""
        user = User(
            email="member@example.com",
            full_name="Team Member",
            hashed_password="hashed_password",
            is_active=True,
        )
        db_session.add(user)
        await db_session.flush()
        return user

    @pytest_asyncio.fixture
    async def test_team_with_owner(
        self,
        db_session: AsyncSession,
        test_team: Team,
        team_owner: User,
    ) -> tuple[Team, User]:
        """Create a team with owner membership."""
        membership = TeamMember(
            team_id=test_team.id,
            user_id=team_owner.id,
            role=TeamRole.OWNER,
        )
        db_session.add(membership)
        await db_session.commit()
        await db_session.refresh(membership)
        await db_session.refresh(test_team)
        return test_team, team_owner

    @pytest_asyncio.fixture
    async def test_team_with_member(
        self,
        db_session: AsyncSession,
        test_team: Team,
        team_member: User,
    ) -> tuple[Team, User]:
        """Create a team with regular member."""
        membership = TeamMember(
            team_id=test_team.id,
            user_id=team_member.id,
            role=TeamRole.MEMBER,
        )
        db_session.add(membership)
        await db_session.commit()
        await db_session.refresh(membership)
        await db_session.refresh(test_team)
        return test_team, team_member

    @pytest.mark.asyncio
    async def test_get_goals_empty_list(
        self,
        project_goal_service,
        test_team_with_member: tuple[Team, User],
    ):
        """Test getting empty goals list."""
        team, member = test_team_with_member
        goals = await project_goal_service.get_project_goals(team.id, member.id)
        assert goals.goals == []
        assert goals.total == 0

    @pytest.mark.asyncio
    async def test_get_goals_unauthorized(
        self,
        project_goal_service,
        test_team: Team,
        team_member: User,
    ):
        """Test getting goals as non-member is forbidden."""
        with pytest.raises(AuthorizationError) as excinfo:
            await project_goal_service.get_project_goals(test_team.id, team_member.id)
        assert excinfo.value.error_code == "NOT_TEAM_MEMBER"

    @pytest.mark.asyncio
    async def test_create_goal_as_owner(
        self,
        project_goal_service,
        test_team_with_owner: tuple[Team, User],
    ):
        """Test goal creation by owner."""
        team, owner = test_team_with_owner

        goal_data = ProjectGoalCreateRequest(
            description="Improve user engagement by 25%",
            priority_weight=8,
            success_metrics="Increase MAU by 25%",
        )

        goal = await project_goal_service.create_project_goal(
            team.id,
            goal_data,
            owner.id,
        )

        assert goal.description == goal_data.description
        assert goal.priority_weight == goal_data.priority_weight
        assert goal.success_metrics == goal_data.success_metrics
        assert goal.team_id == team.id
        assert goal.author_id == owner.id
        assert goal.created_by == owner.id
        assert goal.updated_by is None

    @pytest.mark.asyncio
    async def test_create_goal_unauthorized(
        self,
        project_goal_service,
        test_team_with_member: tuple[Team, User],
    ):
        """Test goal creation by regular member is forbidden."""
        team, member = test_team_with_member

        goal_data = ProjectGoalCreateRequest(
            description="Test goal",
            priority_weight=5,
        )

        with pytest.raises(AuthorizationError) as excinfo:
            await project_goal_service.create_project_goal(
                team.id,
                goal_data,
                member.id,
            )
        assert excinfo.value.error_code == "INSUFFICIENT_PERMISSIONS"

    @pytest.mark.asyncio
    async def test_create_duplicate_goal(
        self,
        db_session: AsyncSession,
        project_goal_service,
        test_team_with_owner: tuple[Team, User],
    ):
        """Test creating duplicate goal description is rejected."""
        team, owner = test_team_with_owner

        # Create initial goal
        goal = ProjectGoal(
            team_id=team.id,
            description="Test goal",
            priority_weight=5,
            author_id=owner.id,
            created_by=owner.id,
        )
        db_session.add(goal)
        await db_session.commit()

        # Try to create duplicate
        goal_data = ProjectGoalCreateRequest(
            description="Test goal",  # Same description
            priority_weight=8,
        )

        with pytest.raises(ValidationError) as excinfo:
            await project_goal_service.create_project_goal(
                team.id,
                goal_data,
                owner.id,
            )
        assert excinfo.value.error_code == "DUPLICATE_GOAL"

    @pytest.mark.asyncio
    async def test_update_goal_as_owner(
        self,
        db_session: AsyncSession,
        project_goal_service,
        test_team_with_owner: tuple[Team, User],
    ):
        """Test goal update by owner."""
        team, owner = test_team_with_owner

        # Create goal
        goal = ProjectGoal(
            team_id=team.id,
            description="Original goal",
            priority_weight=5,
            author_id=owner.id,
            created_by=owner.id,
        )
        db_session.add(goal)
        await db_session.commit()

        # Update goal
        update_data = ProjectGoalUpdateRequest(
            description="Updated goal",
            priority_weight=8,
            success_metrics="New metrics",
        )

        updated_goal = await project_goal_service.update_project_goal(
            team.id,
            goal.id,
            update_data,
            owner.id,
        )

        assert updated_goal.description == update_data.description
        assert updated_goal.priority_weight == update_data.priority_weight
        assert updated_goal.success_metrics == update_data.success_metrics
        assert updated_goal.updated_by == owner.id

    @pytest.mark.asyncio
    async def test_update_goal_unauthorized(
        self,
        db_session: AsyncSession,
        project_goal_service,
        test_team_with_member: tuple[Team, User],
        team_owner: User,
    ):
        """Test goal update by regular member is forbidden."""
        team, member = test_team_with_member

        # Create goal by owner
        goal = ProjectGoal(
            team_id=team.id,
            description="Test goal",
            priority_weight=5,
            author_id=team_owner.id,
            created_by=team_owner.id,
        )
        db_session.add(goal)
        await db_session.commit()

        # Try to update as member
        update_data = ProjectGoalUpdateRequest(description="Updated goal")

        with pytest.raises(AuthorizationError) as excinfo:
            await project_goal_service.update_project_goal(
                team.id,
                goal.id,
                update_data,
                member.id,
            )
        assert excinfo.value.error_code == "INSUFFICIENT_PERMISSIONS"

    @pytest.mark.asyncio
    async def test_update_nonexistent_goal(
        self,
        project_goal_service,
        test_team_with_owner: tuple[Team, User],
    ):
        """Test updating nonexistent goal fails."""
        team, owner = test_team_with_owner

        import uuid

        nonexistent_id = uuid.uuid4()
        update_data = ProjectGoalUpdateRequest(description="Test goal")

        with pytest.raises(ValidationError) as excinfo:
            await project_goal_service.update_project_goal(
                team.id,
                nonexistent_id,
                update_data,
                owner.id,
            )
        assert excinfo.value.error_code == "GOAL_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_delete_goal_as_owner(
        self,
        db_session: AsyncSession,
        project_goal_service,
        test_team_with_owner: tuple[Team, User],
    ):
        """Test goal deletion by owner."""
        team, owner = test_team_with_owner

        # Create goal
        goal = ProjectGoal(
            team_id=team.id,
            description="Test goal",
            priority_weight=5,
            author_id=owner.id,
            created_by=owner.id,
        )
        db_session.add(goal)
        await db_session.commit()

        # Delete goal
        await project_goal_service.delete_project_goal(team.id, goal.id, owner.id)

        # Verify deletion
        result = await db_session.get(ProjectGoal, goal.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_goal_unauthorized(
        self,
        db_session: AsyncSession,
        project_goal_service,
        test_team_with_member: tuple[Team, User],
        team_owner: User,
    ):
        """Test goal deletion by regular member is forbidden."""
        team, member = test_team_with_member

        # Create goal by owner
        goal = ProjectGoal(
            team_id=team.id,
            description="Test goal",
            priority_weight=5,
            author_id=team_owner.id,
            created_by=team_owner.id,
        )
        db_session.add(goal)
        await db_session.commit()

        # Try to delete as member
        with pytest.raises(AuthorizationError) as excinfo:
            await project_goal_service.delete_project_goal(team.id, goal.id, member.id)
        assert excinfo.value.error_code == "INSUFFICIENT_PERMISSIONS"

        # Verify goal still exists
        result = await db_session.get(ProjectGoal, goal.id)
        assert result is not None

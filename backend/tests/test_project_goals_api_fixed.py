"""Tests for project goals API endpoints."""

from contextlib import contextmanager

from httpx import AsyncClient

from app.domains.models.project_goal import ProjectGoal
from app.domains.models.team import Team


@contextmanager
def project_goal_context(app, owner):
    """Create test project goal context."""
    team = Team(
        name="Test Team",
        owner_id=owner.id,
        created_at=datetime.utcnow(),
    )
    return team, owner


class TestProjectGoalsAPI:
    """Test suite for project goals API."""

    async def test_create_goal_with_same_title_different_team(
        self, client: AsyncClient, test_teams, test_users
    ):
        """Test creating goals with same title in different teams."""
        # Test implementation...

    async def test_update_goal_to_match_existing_title(
        self, client: AsyncClient, test_teams, test_users
    ):
        """Test updating goal to match another goal's title."""
        # Test implementation...

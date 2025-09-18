"""Integration tests for the edit work item feature end-to-end flow."""

import uuid

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.models.team import Team, TeamMember
from app.domains.models.user import User
from app.domains.models.work_item import WorkItem, WorkItemStatus, WorkItemType


class TestEditWorkItemIntegration:
    """Test suite for edit work item end-to-end integration."""

    @pytest.fixture
    async def setup_test_data(self, db_session: AsyncSession):
        """Set up test data for integration tests."""
        # Create user
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            name="Test User",
        )
        db_session.add(user)

        # Create team
        team = Team(
            id=uuid.uuid4(),
            name="Test Team",
            owner_id=user.id,
        )
        db_session.add(team)

        # Create team membership
        team_member = TeamMember(
            team_id=team.id,
            user_id=user.id,
            role="owner",
        )
        db_session.add(team_member)

        # Create work item
        work_item = WorkItem(
            id=uuid.uuid4(),
            team_id=team.id,
            author_id=user.id,
            title="Original Work Item",
            description="Original description",
            type=WorkItemType.STORY,
            status=WorkItemStatus.BACKLOG,
            priority=1.0,
            story_points=5,
        )
        db_session.add(work_item)

        await db_session.commit()
        await db_session.refresh(user)
        await db_session.refresh(team)
        await db_session.refresh(work_item)

        return {
            "user": user,
            "team": team,
            "work_item": work_item,
        }

    async def test_complete_edit_work_item_flow(
        self,
        async_client: AsyncClient,
        setup_test_data: dict,
        db_session: AsyncSession,
    ):
        """Test the complete edit work item flow from request to database update."""
        user = setup_test_data["user"]
        team = setup_test_data["team"]
        work_item = setup_test_data["work_item"]

        # Authenticate user (mocked in test setup)
        headers = {"Authorization": f"Bearer {user.id}"}

        # Prepare update data
        update_data = {
            "title": "Updated Work Item Title",
            "description": "Updated description with more details",
            "status": "todo",
            "priority": 3.5,
            "story_points": 8,
        }

        # Make PATCH request
        response = await async_client.patch(
            f"/api/v1/teams/{team.id}/work-items/{work_item.id}",
            json=update_data,
            headers=headers,
        )

        # Verify response
        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert response_data["id"] == str(work_item.id)
        assert response_data["title"] == "Updated Work Item Title"
        assert response_data["description"] == "Updated description with more details"
        assert response_data["status"] == "todo"
        assert response_data["priority"] == 3.5
        assert response_data["story_points"] == 8
        assert response_data["updated_at"] is not None

        # Verify database was updated
        await db_session.refresh(work_item)
        assert work_item.title == "Updated Work Item Title"
        assert work_item.description == "Updated description with more details"
        assert work_item.status == WorkItemStatus.TODO
        assert work_item.priority == 3.5
        assert work_item.story_points == 8

    async def test_edit_work_item_authorization_flow(
        self,
        async_client: AsyncClient,
        setup_test_data: dict,
    ):
        """Test authorization flow for edit work item."""
        team = setup_test_data["team"]
        work_item = setup_test_data["work_item"]

        # Create unauthorized user
        unauthorized_user = User(
            id=uuid.uuid4(),
            email="unauthorized@example.com",
            name="Unauthorized User",
        )

        headers = {"Authorization": f"Bearer {unauthorized_user.id}"}

        update_data = {"title": "Should not work"}

        # Make request as unauthorized user
        response = await async_client.patch(
            f"/api/v1/teams/{team.id}/work-items/{work_item.id}",
            json=update_data,
            headers=headers,
        )

        # Should be forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "access_denied" in response.json()["detail"]["error"]

    async def test_edit_work_item_validation_flow(
        self,
        async_client: AsyncClient,
        setup_test_data: dict,
    ):
        """Test validation flow for edit work item."""
        user = setup_test_data["user"]
        team = setup_test_data["team"]
        work_item = setup_test_data["work_item"]

        headers = {"Authorization": f"Bearer {user.id}"}

        # Test with invalid data
        invalid_data = {
            "priority": -1.0,  # Negative priority should be invalid
        }

        response = await async_client.patch(
            f"/api/v1/teams/{team.id}/work-items/{work_item.id}",
            json=invalid_data,
            headers=headers,
        )

        # Should fail validation
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_edit_work_item_partial_update_flow(
        self,
        async_client: AsyncClient,
        setup_test_data: dict,
        db_session: AsyncSession,
    ):
        """Test partial update flow - only updating specific fields."""
        user = setup_test_data["user"]
        team = setup_test_data["team"]
        work_item = setup_test_data["work_item"]

        headers = {"Authorization": f"Bearer {user.id}"}

        # Get original values
        original_title = work_item.title
        original_description = work_item.description
        original_type = work_item.type

        # Update only status and priority
        update_data = {
            "status": "in_progress",
            "priority": 5.0,
        }

        response = await async_client.patch(
            f"/api/v1/teams/{team.id}/work-items/{work_item.id}",
            json=update_data,
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify only specified fields were updated
        await db_session.refresh(work_item)
        assert work_item.status == WorkItemStatus.IN_PROGRESS
        assert work_item.priority == 5.0

        # Other fields should remain unchanged
        assert work_item.title == original_title
        assert work_item.description == original_description
        assert work_item.type == original_type

    async def test_edit_work_item_not_found_flow(
        self,
        async_client: AsyncClient,
        setup_test_data: dict,
    ):
        """Test work item not found flow."""
        user = setup_test_data["user"]
        team = setup_test_data["team"]
        non_existent_id = uuid.uuid4()

        headers = {"Authorization": f"Bearer {user.id}"}

        update_data = {"title": "Should not work"}

        response = await async_client.patch(
            f"/api/v1/teams/{team.id}/work-items/{non_existent_id}",
            json=update_data,
            headers=headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "work_item_not_found" in response.json()["detail"]["error"]

    async def test_edit_work_item_performance(
        self,
        async_client: AsyncClient,
        setup_test_data: dict,
    ):
        """Test that edit work item meets performance requirements."""
        user = setup_test_data["user"]
        team = setup_test_data["team"]
        work_item = setup_test_data["work_item"]

        headers = {"Authorization": f"Bearer {user.id}"}

        update_data = {
            "title": "Performance Test Update",
            "priority": 2.5,
        }

        # Measure response time
        import time

        start_time = time.time()

        response = await async_client.patch(
            f"/api/v1/teams/{team.id}/work-items/{work_item.id}",
            json=update_data,
            headers=headers,
        )

        end_time = time.time()
        duration = end_time - start_time

        # Verify success and performance
        assert response.status_code == status.HTTP_200_OK
        assert duration < 1.0, f"Response took {duration:.3f} seconds, expected <1.0"

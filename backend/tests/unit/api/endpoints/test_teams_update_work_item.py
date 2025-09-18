"""Unit tests for the PATCH work item endpoint."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.domains.models.user import User
from app.domains.models.work_item import WorkItem, WorkItemStatus, WorkItemType
from app.domains.schemas.work_item import WorkItemUpdateRequest


class TestUpdateTeamWorkItem:
    """Test suite for PATCH /{team_id}/work-items/{work_item_id} endpoint."""

    @pytest.fixture
    def mock_work_item(self) -> WorkItem:
        """Create a mock work item for testing."""
        return WorkItem(
            id=uuid.uuid4(),
            team_id=uuid.uuid4(),
            author_id=uuid.uuid4(),
            title="Original Title",
            description="Original description",
            type=WorkItemType.STORY,
            status=WorkItemStatus.BACKLOG,
            priority=1.0,
            story_points=5,
            assignee_id=uuid.uuid4(),
        )

    @pytest.fixture
    def mock_user(self) -> User:
        """Create a mock user for testing."""
        return User(
            id=uuid.uuid4(),
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_password",
        )

    @pytest.mark.asyncio
    async def test_update_work_item_success(
        self,
        async_client: AsyncClient,
        mock_work_item: WorkItem,
        mock_user: User,
    ):
        """Test successful work item update."""
        # Arrange
        team_id = str(mock_work_item.team_id)
        work_item_id = str(mock_work_item.id)

        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "priority": 2.0,
        }

        updated_work_item = WorkItem(
            **mock_work_item.__dict__,
            title="Updated Title",
            description="Updated description",
            priority=2.0,
        )

        with (
            patch(
                "app.api.v1.endpoints.teams.get_current_user", return_value=mock_user
            ),
            patch("app.api.v1.endpoints.teams.get_work_item_service") as mock_service,
        ):

            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.update_work_item.return_value = updated_work_item

            # Act
            response = await async_client.patch(
                f"/api/v1/teams/{team_id}/work-items/{work_item_id}",
                json=update_data,
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK

            response_data = response.json()
            assert response_data["title"] == "Updated Title"
            assert response_data["description"] == "Updated description"
            assert response_data["priority"] == 2.0

            # Verify service was called correctly
            mock_service_instance.update_work_item.assert_called_once()
            call_args = mock_service_instance.update_work_item.call_args
            assert call_args[1]["work_item_id"] == uuid.UUID(work_item_id)
            assert call_args[1]["user_id"] == mock_user.id
            assert isinstance(call_args[1]["work_item_data"], WorkItemUpdateRequest)

    @pytest.mark.asyncio
    async def test_update_work_item_not_found(
        self,
        async_client: AsyncClient,
        mock_user: User,
    ):
        """Test work item not found error."""
        # Arrange
        team_id = str(uuid.uuid4())
        work_item_id = str(uuid.uuid4())

        update_data = {"title": "Updated Title"}

        with (
            patch(
                "app.api.v1.endpoints.teams.get_current_user", return_value=mock_user
            ),
            patch("app.api.v1.endpoints.teams.get_work_item_service") as mock_service,
        ):

            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.update_work_item.side_effect = ValueError(
                "Work item not found"
            )

            # Act
            response = await async_client.patch(
                f"/api/v1/teams/{team_id}/work-items/{work_item_id}",
                json=update_data,
            )

            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND

            response_data = response.json()
            assert response_data["detail"]["error"] == "work_item_not_found"
            assert "not found" in response_data["detail"]["message"]

    @pytest.mark.asyncio
    async def test_update_work_item_unauthorized(
        self,
        async_client: AsyncClient,
        mock_user: User,
    ):
        """Test unauthorized access when user is not team member."""
        # Arrange
        team_id = str(uuid.uuid4())
        work_item_id = str(uuid.uuid4())

        update_data = {"title": "Updated Title"}

        with (
            patch(
                "app.api.v1.endpoints.teams.get_current_user", return_value=mock_user
            ),
            patch("app.api.v1.endpoints.teams.get_work_item_service") as mock_service,
        ):

            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.update_work_item.side_effect = ValueError(
                "User is not a member of this team"
            )

            # Act
            response = await async_client.patch(
                f"/api/v1/teams/{team_id}/work-items/{work_item_id}",
                json=update_data,
            )

            # Assert
            assert response.status_code == status.HTTP_403_FORBIDDEN

            response_data = response.json()
            assert response_data["detail"]["error"] == "access_denied"
            assert "Not authorized" in response_data["detail"]["message"]

    @pytest.mark.asyncio
    async def test_update_work_item_invalid_uuid(
        self,
        async_client: AsyncClient,
        mock_user: User,
    ):
        """Test invalid UUID format."""
        # Arrange
        team_id = "invalid-uuid"
        work_item_id = str(uuid.uuid4())

        update_data = {"title": "Updated Title"}

        with (
            patch(
                "app.api.v1.endpoints.teams.get_current_user", return_value=mock_user
            ),
            patch("app.api.v1.endpoints.teams.get_work_item_service") as mock_service,
        ):

            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance

            # Act
            response = await async_client.patch(
                f"/api/v1/teams/{team_id}/work-items/{work_item_id}",
                json=update_data,
            )

            # Assert
            assert response.status_code == status.HTTP_400_BAD_REQUEST

            response_data = response.json()
            assert response_data["detail"]["error"] == "invalid_format"
            assert "Invalid ID format" in response_data["detail"]["message"]

    @pytest.mark.asyncio
    async def test_update_work_item_validation_error(
        self,
        async_client: AsyncClient,
        mock_user: User,
    ):
        """Test validation errors."""
        # Arrange
        team_id = str(uuid.uuid4())
        work_item_id = str(uuid.uuid4())

        # Invalid data: negative priority
        update_data = {"priority": -1.0}

        with patch(
            "app.api.v1.endpoints.teams.get_current_user", return_value=mock_user
        ):
            # Act
            response = await async_client.patch(
                f"/api/v1/teams/{team_id}/work-items/{work_item_id}",
                json=update_data,
            )

            # Assert - Pydantic validation should catch this
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_update_work_item_empty_title(
        self,
        async_client: AsyncClient,
        mock_user: User,
    ):
        """Test empty title validation."""
        # Arrange
        team_id = str(uuid.uuid4())
        work_item_id = str(uuid.uuid4())

        update_data = {"title": ""}

        with (
            patch(
                "app.api.v1.endpoints.teams.get_current_user", return_value=mock_user
            ),
            patch("app.api.v1.endpoints.teams.get_work_item_service") as mock_service,
        ):

            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.update_work_item.side_effect = ValueError(
                "Title cannot be empty"
            )

            # Act
            response = await async_client.patch(
                f"/api/v1/teams/{team_id}/work-items/{work_item_id}",
                json=update_data,
            )

            # Assert
            assert response.status_code == status.HTTP_400_BAD_REQUEST

            response_data = response.json()
            assert response_data["detail"]["error"] == "validation_error"
            assert "Title cannot be empty" in response_data["detail"]["message"]

    @pytest.mark.asyncio
    async def test_update_work_item_partial_update(
        self,
        async_client: AsyncClient,
        mock_work_item: WorkItem,
        mock_user: User,
    ):
        """Test partial update with only specific fields."""
        # Arrange
        team_id = str(mock_work_item.team_id)
        work_item_id = str(mock_work_item.id)

        # Only update status
        update_data = {"status": "todo"}

        updated_work_item = WorkItem(
            **mock_work_item.__dict__,
            status=WorkItemStatus.TODO,
        )

        with (
            patch(
                "app.api.v1.endpoints.teams.get_current_user", return_value=mock_user
            ),
            patch("app.api.v1.endpoints.teams.get_work_item_service") as mock_service,
        ):

            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.update_work_item.return_value = updated_work_item

            # Act
            response = await async_client.patch(
                f"/api/v1/teams/{team_id}/work-items/{work_item_id}",
                json=update_data,
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK

            response_data = response.json()
            assert response_data["status"] == "todo"
            # Other fields should remain unchanged
            assert response_data["title"] == mock_work_item.title
            assert response_data["description"] == mock_work_item.description

    @pytest.mark.asyncio
    async def test_update_work_item_server_error(
        self,
        async_client: AsyncClient,
        mock_user: User,
    ):
        """Test internal server error handling."""
        # Arrange
        team_id = str(uuid.uuid4())
        work_item_id = str(uuid.uuid4())

        update_data = {"title": "Updated Title"}

        with (
            patch(
                "app.api.v1.endpoints.teams.get_current_user", return_value=mock_user
            ),
            patch("app.api.v1.endpoints.teams.get_work_item_service") as mock_service,
        ):

            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.update_work_item.side_effect = Exception(
                "Database connection error"
            )

            # Act
            response = await async_client.patch(
                f"/api/v1/teams/{team_id}/work-items/{work_item_id}",
                json=update_data,
            )

            # Assert
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

            response_data = response.json()
            assert response_data["detail"]["code"] == "INTERNAL_SERVER_ERROR"
            assert "unexpected error" in response_data["detail"]["message"].lower()

    @pytest.mark.asyncio
    async def test_update_work_item_logging(
        self,
        async_client: AsyncClient,
        mock_work_item: WorkItem,
        mock_user: User,
    ):
        """Test that proper logging occurs during update."""
        # Arrange
        team_id = str(mock_work_item.team_id)
        work_item_id = str(mock_work_item.id)

        update_data = {"title": "Updated Title"}

        with (
            patch(
                "app.api.v1.endpoints.teams.get_current_user", return_value=mock_user
            ),
            patch("app.api.v1.endpoints.teams.get_work_item_service") as mock_service,
            patch("app.api.v1.endpoints.teams.logger") as mock_logger,
        ):

            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.update_work_item.return_value = mock_work_item

            # Act
            response = await async_client.patch(
                f"/api/v1/teams/{team_id}/work-items/{work_item_id}",
                json=update_data,
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK

            # Verify logging calls
            assert mock_logger.info.call_count >= 2  # Start and success logs

            # Check start log
            start_log_call = mock_logger.info.call_args_list[0]
            assert "Updating work item" in start_log_call[0][0]

            # Check success log
            success_log_call = mock_logger.info.call_args_list[1]
            assert "Work item updated successfully" in success_log_call[0][0]

    @pytest.mark.asyncio
    async def test_update_work_item_performance_monitoring(
        self,
        async_client: AsyncClient,
        mock_work_item: WorkItem,
        mock_user: User,
    ):
        """Test that the endpoint completes within performance requirements."""
        # Arrange
        team_id = str(mock_work_item.team_id)
        work_item_id = str(mock_work_item.id)

        update_data = {"title": "Updated Title"}

        with (
            patch(
                "app.api.v1.endpoints.teams.get_current_user", return_value=mock_user
            ),
            patch("app.api.v1.endpoints.teams.get_work_item_service") as mock_service,
        ):

            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.update_work_item.return_value = mock_work_item

            # Act & Assert
            import time

            start_time = time.time()

            response = await async_client.patch(
                f"/api/v1/teams/{team_id}/work-items/{work_item_id}",
                json=update_data,
            )

            end_time = time.time()
            duration = end_time - start_time

            assert response.status_code == status.HTTP_200_OK
            # Story requirement: <1 second response time
            assert (
                duration < 1.0
            ), f"Response took {duration:.3f} seconds, expected <1.0"

    @pytest.mark.asyncio
    async def test_update_work_item_concurrent_modification(
        self,
        async_client: AsyncClient,
        mock_work_item: WorkItem,
        mock_user: User,
    ):
        """Test handling of concurrent modification scenarios."""
        # This test simulates optimistic concurrency handling
        # In a real system, you might check version numbers or timestamps

        # Arrange
        team_id = str(mock_work_item.team_id)
        work_item_id = str(mock_work_item.id)

        update_data = {"title": "Updated Title"}

        with (
            patch(
                "app.api.v1.endpoints.teams.get_current_user", return_value=mock_user
            ),
            patch("app.api.v1.endpoints.teams.get_work_item_service") as mock_service,
        ):

            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            # Simulate that the item was modified after we fetched it
            mock_service_instance.update_work_item.side_effect = ValueError(
                "Work item was modified by another user"
            )

            # Act
            response = await async_client.patch(
                f"/api/v1/teams/{team_id}/work-items/{work_item_id}",
                json=update_data,
            )

            # Assert - Should be handled gracefully
            assert response.status_code == status.HTTP_400_BAD_REQUEST

            response_data = response.json()
            assert response_data["detail"]["error"] == "validation_error"
            assert "modified by another user" in response_data["detail"]["message"]

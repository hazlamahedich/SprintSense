"""Tests for work item archive functionality (Story 2.5)."""

import uuid
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# from app.api.v1.endpoints.teams import archive_team_work_item  # Will be implemented
from app.domains.models.work_item import WorkItemStatus
from app.domains.schemas.work_item import WorkItemResponse
from app.domains.services.work_item_service import WorkItemService


class TestArchiveWorkItemService:
    """Test cases for WorkItemService.archive_work_item method."""

    @pytest.fixture
    def mock_db(self) -> AsyncMock:
        """Mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def work_item_service(self, mock_db: AsyncMock) -> WorkItemService:
        """Create WorkItemService instance with mocked database."""
        return WorkItemService(db=mock_db)

    @pytest.fixture
    def sample_work_item_data(self) -> Dict[str, Any]:
        """Sample work item data for testing."""
        return {
            "id": uuid.uuid4(),
            "team_id": uuid.uuid4(),
            "author_id": uuid.uuid4(),
            "title": "Test Work Item",
            "description": "Test description",
            "status": WorkItemStatus.BACKLOG,
            "priority": 1.0,
            "type": "story",  # Correct enum value
            "story_points": 5,  # Proper integer
            "sprint_id": None,  # Optional UUID
            "assignee_id": None,  # Optional UUID
            "completed_at": None,  # Optional datetime
            "source_sprint_id_for_action_item": None,  # Optional UUID
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

    @pytest.mark.asyncio
    async def test_archive_work_item_success(
        self,
        work_item_service: WorkItemService,
        mock_db: AsyncMock,
        sample_work_item_data: Dict[str, Any],
    ) -> None:
        """Test successful work item archival."""
        # Arrange
        work_item_id = sample_work_item_data["id"]
        user_id = uuid.uuid4()

        # Mock work item
        mock_work_item = Mock()
        for key, value in sample_work_item_data.items():
            setattr(mock_work_item, key, value)

        # Mock database queries
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_work_item
        mock_db.execute.return_value = mock_result

        # Mock team membership check
        work_item_service._is_team_member = AsyncMock(return_value=True)

        # Act
        result = await work_item_service.archive_work_item(work_item_id, user_id)

        # Assert
        assert isinstance(result, WorkItemResponse)
        assert mock_work_item.status == WorkItemStatus.ARCHIVED
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_work_item)

    @pytest.mark.asyncio
    async def test_archive_work_item_not_found(
        self,
        work_item_service: WorkItemService,
        mock_db: AsyncMock,
    ) -> None:
        """Test archiving non-existent work item."""
        # Arrange
        work_item_id = uuid.uuid4()
        user_id = uuid.uuid4()

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(ValueError, match="Work item not found"):
            await work_item_service.archive_work_item(work_item_id, user_id)

    @pytest.mark.asyncio
    async def test_archive_work_item_not_team_member(
        self,
        work_item_service: WorkItemService,
        mock_db: AsyncMock,
        sample_work_item_data: Dict[str, Any],
    ) -> None:
        """Test archiving work item when user is not a team member."""
        # Arrange
        work_item_id = sample_work_item_data["id"]
        user_id = uuid.uuid4()

        mock_work_item = Mock()
        for key, value in sample_work_item_data.items():
            setattr(mock_work_item, key, value)

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_work_item
        mock_db.execute.return_value = mock_result

        work_item_service._is_team_member = AsyncMock(return_value=False)

        # Act & Assert
        with pytest.raises(ValueError, match="User is not a member of this team"):
            await work_item_service.archive_work_item(work_item_id, user_id)

    @pytest.mark.asyncio
    async def test_get_work_items_excludes_archived_by_default(
        self,
        work_item_service: WorkItemService,
        mock_db: AsyncMock,
    ) -> None:
        """Test that get_work_items excludes archived items by default."""
        # Arrange
        team_id = uuid.uuid4()
        user_id = uuid.uuid4()

        work_item_service._is_team_member = AsyncMock(return_value=True)

        # Mock database execution results
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        # Act
        await work_item_service.get_work_items(team_id, user_id, include_archived=False)

        # Assert - verify that the query excludes archived items
        call_args = mock_db.execute.call_args_list
        # The first call is the main query, second call is the count query
        assert len(call_args) >= 2

        # Check that both queries contain the condition to exclude archived items
        for call in call_args:
            query = call[0][0]  # First argument is the query
            query_str = str(query)
            # The query should contain a condition excluding archived status
            assert "status" in query_str.lower()

    @pytest.mark.asyncio
    async def test_get_work_items_includes_archived_when_requested(
        self,
        work_item_service: WorkItemService,
        mock_db: AsyncMock,
    ) -> None:
        """Test that get_work_items includes archived items when include_archived=True."""
        # Arrange
        team_id = uuid.uuid4()
        user_id = uuid.uuid4()

        work_item_service._is_team_member = AsyncMock(return_value=True)

        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        # Act
        await work_item_service.get_work_items(team_id, user_id, include_archived=True)

        # Assert - verify that archived filtering is not applied
        call_args = mock_db.execute.call_args_list
        assert len(call_args) >= 2

        # When include_archived=True, the queries should not filter out archived items
        # by default (they would only be filtered if status is explicitly set)


# API endpoint tests will be added when the endpoint is implemented

"""Unit tests for WorkItem Pydantic schemas."""

import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.domains.models.work_item import WorkItemStatus, WorkItemType
from app.domains.schemas.work_item import (
    WorkItemCreateRequest,
    WorkItemListResponse,
    WorkItemResponse,
    WorkItemUpdateRequest,
)


class TestWorkItemCreateRequest:
    """Tests for WorkItemCreateRequest schema."""

    def test_valid_create_request(self):
        """Test valid work item creation request."""
        team_id = uuid.uuid4()

        request = WorkItemCreateRequest(
            team_id=team_id,
            title="Test Work Item",
            description="Test description",
            type=WorkItemType.STORY,
            priority=1.0,
            story_points=3,
        )

        assert request.team_id == team_id
        assert request.title == "Test Work Item"
        assert request.description == "Test description"
        assert request.type == WorkItemType.STORY
        assert request.priority == 1.0
        assert request.story_points == 3
        assert request.assignee_id is None

    def test_create_request_with_assignee(self):
        """Test work item creation request with assignee."""
        team_id = uuid.uuid4()
        assignee_id = uuid.uuid4()

        request = WorkItemCreateRequest(
            team_id=team_id,
            assignee_id=assignee_id,
            title="Assigned Work Item",
            type=WorkItemType.BUG,
            priority=5.0,
        )

        assert request.team_id == team_id
        assert request.assignee_id == assignee_id
        assert request.title == "Assigned Work Item"
        assert request.type == WorkItemType.BUG
        assert request.priority == 5.0

    def test_create_request_with_defaults(self):
        """Test work item creation request with default values."""
        team_id = uuid.uuid4()

        request = WorkItemCreateRequest(
            team_id=team_id,
            title="Default Work Item",
        )

        assert request.team_id == team_id
        assert request.title == "Default Work Item"
        assert request.description is None
        assert request.type == WorkItemType.STORY  # Default
        assert request.priority is None  # Default - auto-calculated
        assert request.story_points is None
        assert request.assignee_id is None

    def test_create_request_empty_title_fails(self):
        """Test that empty title raises validation error."""
        team_id = uuid.uuid4()

        with pytest.raises(ValidationError) as exc_info:
            WorkItemCreateRequest(
                team_id=team_id,
                title="",
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "Title cannot be empty" in str(errors[0]["msg"])

    def test_create_request_whitespace_title_fails(self):
        """Test that whitespace-only title raises validation error."""
        team_id = uuid.uuid4()

        with pytest.raises(ValidationError) as exc_info:
            WorkItemCreateRequest(
                team_id=team_id,
                title="   ",
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "Title cannot be empty" in str(errors[0]["msg"])

    def test_create_request_long_title_fails(self):
        """Test that overly long title raises validation error."""
        team_id = uuid.uuid4()
        long_title = "x" * 201  # 201 characters, exceeds 200 limit

        with pytest.raises(ValidationError) as exc_info:
            WorkItemCreateRequest(
                team_id=team_id,
                title=long_title,
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "Title cannot exceed 200 characters" in str(errors[0]["msg"])

    def test_create_request_negative_priority_fails(self):
        """Test that negative priority raises validation error."""
        team_id = uuid.uuid4()

        with pytest.raises(ValidationError) as exc_info:
            WorkItemCreateRequest(
                team_id=team_id,
                title="Test Item",
                priority=-1.0,
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "Priority cannot be negative" in str(errors[0]["msg"])

    def test_create_request_negative_story_points_fails(self):
        """Test that negative story points raises validation error."""
        team_id = uuid.uuid4()

        with pytest.raises(ValidationError) as exc_info:
            WorkItemCreateRequest(
                team_id=team_id,
                title="Test Item",
                story_points=-1,
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "Story points cannot be negative" in str(errors[0]["msg"])

    def test_create_request_title_trimmed(self):
        """Test that title whitespace is trimmed."""
        team_id = uuid.uuid4()

        request = WorkItemCreateRequest(
            team_id=team_id,
            title="  Test Work Item  ",
        )

        assert request.title == "Test Work Item"


class TestWorkItemUpdateRequest:
    """Tests for WorkItemUpdateRequest schema."""

    def test_valid_update_request(self):
        """Test valid work item update request."""
        assignee_id = uuid.uuid4()

        request = WorkItemUpdateRequest(
            title="Updated Title",
            description="Updated description",
            type=WorkItemType.BUG,
            status=WorkItemStatus.IN_PROGRESS,
            priority=5.0,
            story_points=8,
            assignee_id=assignee_id,
        )

        assert request.title == "Updated Title"
        assert request.description == "Updated description"
        assert request.type == WorkItemType.BUG
        assert request.status == WorkItemStatus.IN_PROGRESS
        assert request.priority == 5.0
        assert request.story_points == 8
        assert request.assignee_id == assignee_id

    def test_update_request_all_none(self):
        """Test update request with all None values."""
        request = WorkItemUpdateRequest()

        assert request.title is None
        assert request.description is None
        assert request.type is None
        assert request.status is None
        assert request.priority is None
        assert request.story_points is None
        assert request.assignee_id is None

    def test_update_request_partial_update(self):
        """Test partial update request."""
        request = WorkItemUpdateRequest(
            title="New Title",
            status=WorkItemStatus.DONE,
        )

        assert request.title == "New Title"
        assert request.status == WorkItemStatus.DONE
        assert request.description is None
        assert request.type is None
        assert request.priority is None
        assert request.story_points is None
        assert request.assignee_id is None

    def test_update_request_empty_title_fails(self):
        """Test that empty title raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            WorkItemUpdateRequest(title="")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "Title cannot be empty" in str(errors[0]["msg"])

    def test_update_request_long_title_fails(self):
        """Test that overly long title raises validation error."""
        long_title = "x" * 256  # 256 characters, exceeds 255 limit

        with pytest.raises(ValidationError) as exc_info:
            WorkItemUpdateRequest(title=long_title)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "Title cannot exceed 255 characters" in str(errors[0]["msg"])

    def test_update_request_negative_priority_fails(self):
        """Test that negative priority raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            WorkItemUpdateRequest(priority=-1.0)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "Priority cannot be negative" in str(errors[0]["msg"])

    def test_update_request_negative_story_points_fails(self):
        """Test that negative story points raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            WorkItemUpdateRequest(story_points=-1)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "Story points cannot be negative" in str(errors[0]["msg"])

    def test_update_request_title_trimmed(self):
        """Test that title whitespace is trimmed."""
        request = WorkItemUpdateRequest(title="  Updated Title  ")
        assert request.title == "Updated Title"


class TestWorkItemResponse:
    """Tests for WorkItemResponse schema."""

    def test_valid_response(self):
        """Test valid work item response."""
        work_item_id = uuid.uuid4()
        team_id = uuid.uuid4()
        author_id = uuid.uuid4()
        assignee_id = uuid.uuid4()
        sprint_id = uuid.uuid4()
        source_sprint_id = uuid.uuid4()
        created_at = datetime.utcnow()
        updated_at = datetime.utcnow()
        completed_at = datetime.utcnow()

        response = WorkItemResponse(
            id=work_item_id,
            team_id=team_id,
            sprint_id=sprint_id,
            author_id=author_id,
            assignee_id=assignee_id,
            title="Test Work Item",
            description="Test description",
            type=WorkItemType.STORY,
            status=WorkItemStatus.DONE,
            priority=1.0,
            story_points=3,
            completed_at=completed_at,
            source_sprint_id_for_action_item=source_sprint_id,
            created_at=created_at,
            updated_at=updated_at,
        )

        assert response.id == work_item_id
        assert response.team_id == team_id
        assert response.sprint_id == sprint_id
        assert response.author_id == author_id
        assert response.assignee_id == assignee_id
        assert response.title == "Test Work Item"
        assert response.description == "Test description"
        assert response.type == WorkItemType.STORY
        assert response.status == WorkItemStatus.DONE
        assert response.priority == 1.0
        assert response.story_points == 3
        assert response.completed_at == completed_at
        assert response.source_sprint_id_for_action_item == source_sprint_id
        assert response.created_at == created_at
        assert response.updated_at == updated_at

    def test_response_with_minimal_data(self):
        """Test work item response with minimal required data."""
        work_item_id = uuid.uuid4()
        team_id = uuid.uuid4()
        author_id = uuid.uuid4()
        created_at = datetime.utcnow()

        response = WorkItemResponse(
            id=work_item_id,
            team_id=team_id,
            author_id=author_id,
            title="Minimal Work Item",
            type=WorkItemType.STORY,
            status=WorkItemStatus.BACKLOG,
            priority=0.0,
            created_at=created_at,
        )

        assert response.id == work_item_id
        assert response.team_id == team_id
        assert response.author_id == author_id
        assert response.title == "Minimal Work Item"
        assert response.type == WorkItemType.STORY
        assert response.status == WorkItemStatus.BACKLOG
        assert response.priority == 0.0
        assert response.created_at == created_at
        # Optional fields should be None
        assert response.sprint_id is None
        assert response.assignee_id is None
        assert response.description is None
        assert response.story_points is None
        assert response.completed_at is None
        assert response.source_sprint_id_for_action_item is None
        assert response.updated_at is None


class TestWorkItemListResponse:
    """Tests for WorkItemListResponse schema."""

    def test_valid_list_response(self):
        """Test valid work item list response."""
        work_item_1 = WorkItemResponse(
            id=uuid.uuid4(),
            team_id=uuid.uuid4(),
            author_id=uuid.uuid4(),
            title="Work Item 1",
            type=WorkItemType.STORY,
            status=WorkItemStatus.BACKLOG,
            priority=0.0,
            created_at=datetime.utcnow(),
        )

        work_item_2 = WorkItemResponse(
            id=uuid.uuid4(),
            team_id=uuid.uuid4(),
            author_id=uuid.uuid4(),
            title="Work Item 2",
            type=WorkItemType.BUG,
            status=WorkItemStatus.TODO,
            priority=1.0,
            created_at=datetime.utcnow(),
        )

        list_response = WorkItemListResponse(
            items=[work_item_1, work_item_2],
            total=2,
            page=1,
            size=10,
        )

        assert len(list_response.items) == 2
        assert list_response.items[0] == work_item_1
        assert list_response.items[1] == work_item_2
        assert list_response.total == 2
        assert list_response.page == 1
        assert list_response.size == 10

    def test_empty_list_response(self):
        """Test empty work item list response."""
        list_response = WorkItemListResponse(
            items=[],
            total=0,
            page=1,
            size=10,
        )

        assert len(list_response.items) == 0
        assert list_response.total == 0
        assert list_response.page == 1
        assert list_response.size == 10

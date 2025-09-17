"""Unit tests for WorkItem model."""

import uuid
from datetime import datetime

import pytest

from app.domains.models.team import Team
from app.domains.models.user import User
from app.domains.models.work_item import WorkItem, WorkItemStatus, WorkItemType


@pytest.fixture
def sample_team():
    """Sample team for testing."""
    return Team(
        id=uuid.uuid4(),
        name="Test Team",
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_user():
    """Sample user for testing."""
    return User(
        id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password",
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_author():
    """Sample author user for testing."""
    return User(
        id=uuid.uuid4(),
        email="author@example.com",
        full_name="Author User",
        hashed_password="hashed_password",
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_work_item(sample_team, sample_author):
    """Sample work item for testing."""
    return WorkItem(
        id=uuid.uuid4(),
        team_id=sample_team.id,
        author_id=sample_author.id,
        title="Test Work Item",
        description="This is a test work item",
        type=WorkItemType.STORY,
        status=WorkItemStatus.BACKLOG,
        priority=1.0,
        story_points=3,
        created_at=datetime.utcnow(),
    )


def test_work_item_creation(sample_work_item):
    """Test work item creation."""
    assert sample_work_item.title == "Test Work Item"
    assert sample_work_item.description == "This is a test work item"
    assert sample_work_item.type == WorkItemType.STORY
    assert sample_work_item.status == WorkItemStatus.BACKLOG
    assert sample_work_item.priority == 1.0
    assert sample_work_item.story_points == 3
    assert sample_work_item.assignee_id is None
    assert sample_work_item.sprint_id is None
    assert sample_work_item.completed_at is None
    assert sample_work_item.source_sprint_id_for_action_item is None


def test_work_item_with_defaults():
    """Test work item creation with default values."""
    team_id = uuid.uuid4()
    author_id = uuid.uuid4()

    work_item = WorkItem(
        team_id=team_id,
        author_id=author_id,
        title="Default Work Item",
        type=WorkItemType.STORY,
        status=WorkItemStatus.BACKLOG,
        priority=0.0,
    )

    assert work_item.title == "Default Work Item"
    assert work_item.description is None
    assert work_item.type == WorkItemType.STORY  # Default value
    assert work_item.status == WorkItemStatus.BACKLOG  # Default value
    assert work_item.priority == 0.0  # Default value
    assert work_item.story_points is None
    assert work_item.assignee_id is None
    assert work_item.sprint_id is None
    assert work_item.completed_at is None
    assert work_item.source_sprint_id_for_action_item is None


def test_work_item_with_assignee(sample_team, sample_author, sample_user):
    """Test work item creation with assignee."""
    work_item = WorkItem(
        team_id=sample_team.id,
        author_id=sample_author.id,
        assignee_id=sample_user.id,
        title="Assigned Work Item",
        type=WorkItemType.BUG,
        status=WorkItemStatus.IN_PROGRESS,
        priority=5.0,
        story_points=8,
    )

    assert work_item.assignee_id == sample_user.id
    assert work_item.type == WorkItemType.BUG
    assert work_item.status == WorkItemStatus.IN_PROGRESS
    assert work_item.priority == 5.0
    assert work_item.story_points == 8


def test_work_item_with_sprint_references():
    """Test work item with sprint-related fields."""
    team_id = uuid.uuid4()
    author_id = uuid.uuid4()
    sprint_id = uuid.uuid4()
    source_sprint_id = uuid.uuid4()

    work_item = WorkItem(
        team_id=team_id,
        author_id=author_id,
        title="Sprint Work Item",
        sprint_id=sprint_id,
        source_sprint_id_for_action_item=source_sprint_id,
        status=WorkItemStatus.DONE,
        completed_at=datetime.utcnow(),
    )

    assert work_item.sprint_id == sprint_id
    assert work_item.source_sprint_id_for_action_item == source_sprint_id
    assert work_item.status == WorkItemStatus.DONE
    assert work_item.completed_at is not None


def test_work_item_type_enum_values():
    """Test that WorkItemType enum has expected values."""
    assert WorkItemType.STORY == "story"
    assert WorkItemType.BUG == "bug"
    assert WorkItemType.TASK == "task"

    # Test all enum values are present
    expected_values = {"story", "bug", "task"}
    actual_values = {item.value for item in WorkItemType}
    assert actual_values == expected_values


def test_work_item_status_enum_values():
    """Test that WorkItemStatus enum has expected values."""
    assert WorkItemStatus.BACKLOG == "backlog"
    assert WorkItemStatus.TODO == "todo"
    assert WorkItemStatus.IN_PROGRESS == "in_progress"
    assert WorkItemStatus.DONE == "done"
    assert WorkItemStatus.ARCHIVED == "archived"

    # Test all enum values are present
    expected_values = {"backlog", "todo", "in_progress", "done", "archived"}
    actual_values = {status.value for status in WorkItemStatus}
    assert actual_values == expected_values


def test_work_item_repr(sample_work_item):
    """Test work item string representation."""
    repr_str = repr(sample_work_item)

    assert "WorkItem" in repr_str
    assert str(sample_work_item.id) in repr_str
    assert "Test Work Item" in repr_str
    assert "WorkItemType.STORY" in repr_str  # Check for enum representation
    assert "WorkItemStatus.BACKLOG" in repr_str  # Check for enum representation


def test_work_item_all_types():
    """Test work item creation with all types."""
    team_id = uuid.uuid4()
    author_id = uuid.uuid4()

    # Test STORY type
    story_item = WorkItem(
        team_id=team_id,
        author_id=author_id,
        title="Story Item",
        type=WorkItemType.STORY,
    )
    assert story_item.type == WorkItemType.STORY

    # Test BUG type
    bug_item = WorkItem(
        team_id=team_id,
        author_id=author_id,
        title="Bug Item",
        type=WorkItemType.BUG,
    )
    assert bug_item.type == WorkItemType.BUG

    # Test TASK type
    task_item = WorkItem(
        team_id=team_id,
        author_id=author_id,
        title="Task Item",
        type=WorkItemType.TASK,
    )
    assert task_item.type == WorkItemType.TASK


def test_work_item_all_statuses():
    """Test work item creation with all statuses."""
    team_id = uuid.uuid4()
    author_id = uuid.uuid4()

    statuses = [
        WorkItemStatus.BACKLOG,
        WorkItemStatus.TODO,
        WorkItemStatus.IN_PROGRESS,
        WorkItemStatus.DONE,
        WorkItemStatus.ARCHIVED,
    ]

    for status in statuses:
        work_item = WorkItem(
            team_id=team_id,
            author_id=author_id,
            title=f"Work Item - {status.value}",
            status=status,
        )
        assert work_item.status == status


def test_work_item_priority_values():
    """Test work item with various priority values."""
    team_id = uuid.uuid4()
    author_id = uuid.uuid4()

    # Test default priority
    default_item = WorkItem(
        team_id=team_id,
        author_id=author_id,
        title="Default Priority",
        type=WorkItemType.STORY,
        status=WorkItemStatus.BACKLOG,
        priority=0.0,
    )
    assert default_item.priority == 0.0

    # Test positive priority
    high_priority_item = WorkItem(
        team_id=team_id,
        author_id=author_id,
        title="High Priority",
        priority=10.5,
    )
    assert high_priority_item.priority == 10.5

    # Test zero priority
    zero_priority_item = WorkItem(
        team_id=team_id,
        author_id=author_id,
        title="Zero Priority",
        priority=0.0,
    )
    assert zero_priority_item.priority == 0.0


def test_work_item_story_points_values():
    """Test work item with various story points values."""
    team_id = uuid.uuid4()
    author_id = uuid.uuid4()

    # Test no story points (None)
    no_points_item = WorkItem(
        team_id=team_id,
        author_id=author_id,
        title="No Points",
    )
    assert no_points_item.story_points is None

    # Test positive story points
    points_item = WorkItem(
        team_id=team_id,
        author_id=author_id,
        title="With Points",
        story_points=5,
    )
    assert points_item.story_points == 5

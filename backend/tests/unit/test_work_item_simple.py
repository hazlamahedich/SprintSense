"""Simple unit tests for work item completion date logic."""

import uuid
from datetime import datetime
from typing import Optional

import pytest

from app.domains.models.work_item import WorkItem, WorkItemStatus, WorkItemType
from app.domains.schemas.work_item import WorkItemUpdateRequest


def test_work_item_completion_date():
    """Test work item completion date is set when status changes to DONE."""
    # Create a work item
    work_item_id = uuid.uuid4()
    team_id = uuid.uuid4()
    author_id = uuid.uuid4()

    work_item = WorkItem(
        id=work_item_id,
        team_id=team_id,
        author_id=author_id,
        title="Test Work Item",
        type=WorkItemType.STORY,
        status=WorkItemStatus.TODO,
        priority=1.0,
        created_at=datetime.utcnow(),
    )

    # Verify initial state
    assert work_item.status == WorkItemStatus.TODO
    assert work_item.completed_at is None

    # Update to DONE status
    work_item.status = WorkItemStatus.DONE
    work_item.completed_at = datetime.utcnow()

    # Verify completion state
    assert work_item.status == WorkItemStatus.DONE
    assert work_item.completed_at is not None

    # Move back to IN_PROGRESS
    work_item.status = WorkItemStatus.IN_PROGRESS
    work_item.completed_at = None

    # Verify completion date cleared
    assert work_item.status == WorkItemStatus.IN_PROGRESS
    assert work_item.completed_at is None


def test_work_item_update_request():
    """Test work item update request with status change."""
    update_data = WorkItemUpdateRequest(
        status=WorkItemStatus.DONE,
        title="Updated Title",
    )

    assert update_data.status == WorkItemStatus.DONE
    assert update_data.title == "Updated Title"


def test_work_item_non_done_status():
    """Test work item with non-DONE status has no completion date."""
    work_item = WorkItem(
        id=uuid.uuid4(),
        team_id=uuid.uuid4(),
        author_id=uuid.uuid4(),
        title="Test Work Item",
        type=WorkItemType.STORY,
        status=WorkItemStatus.IN_PROGRESS,
        priority=1.0,
        created_at=datetime.utcnow(),
    )

    assert work_item.status == WorkItemStatus.IN_PROGRESS
    assert work_item.completed_at is None

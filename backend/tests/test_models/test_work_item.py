"""Unit tests for work item model."""

import uuid
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.models.work_item import WorkItem, WorkItemStatus, WorkItemType


@pytest.mark.asyncio
async def test_work_item_status_completion_date(db: AsyncSession):
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

    db.add(work_item)
    await db.commit()

    # Verify initial state
    assert work_item.status == WorkItemStatus.TODO
    assert work_item.completed_at is None

    # Update to DONE status
    work_item.status = WorkItemStatus.DONE
    work_item.completed_at = datetime.utcnow()
    await db.commit()

    # Verify completion state
    assert work_item.status == WorkItemStatus.DONE
    assert work_item.completed_at is not None

    # Move back to IN_PROGRESS
    work_item.status = WorkItemStatus.IN_PROGRESS
    work_item.completed_at = None
    await db.commit()

    # Verify completion date cleared
    assert work_item.status == WorkItemStatus.IN_PROGRESS
    assert work_item.completed_at is None


@pytest.mark.asyncio
async def test_work_item_non_done_status(db: AsyncSession):
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

    db.add(work_item)
    await db.commit()

    assert work_item.status == WorkItemStatus.IN_PROGRESS
    assert work_item.completed_at is None

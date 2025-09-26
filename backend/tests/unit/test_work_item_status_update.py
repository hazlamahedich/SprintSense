"""Unit tests for work item status updates and completion date handling."""

import uuid
from datetime import datetime

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.models.team import Team, TeamMember, TeamRole
from app.domains.models.user import User
from app.domains.models.work_item import WorkItem, WorkItemStatus, WorkItemType
from app.domains.schemas.work_item import WorkItemUpdateRequest
from app.domains.services.work_item_service import WorkItemService


@pytest_asyncio.fixture
async def test_team(db: AsyncSession) -> Team:
    """Create a test team."""
    team = Team(
        id=uuid.uuid4(),
        name="Test Team",
        created_at=datetime.utcnow(),
    )
    db.add(team)
    await db.commit()
    return team


@pytest_asyncio.fixture
async def test_user_with_team_membership(db: AsyncSession, test_team: Team) -> User:
    """Create a test user."""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        hashed_password="test_hash",
        created_at=datetime.utcnow(),
    )
    db.add(user)
    await db.commit()

    # Add team membership
    team_member = TeamMember(
        team_id=test_team.id,
        user_id=user.id,
        role=TeamRole.OWNER,
    )
    db.add(team_member)
    await db.commit()

    return user


@pytest_asyncio.fixture
async def test_work_item(
    db: AsyncSession, test_team: Team, test_user_with_team_membership: User
) -> WorkItem:
    """Create a test work item."""
    work_item = WorkItem(
        id=uuid.uuid4(),
        team_id=test_team.id,
        author_id=test_user_with_team_membership.id,
        title="Test Work Item",
        type=WorkItemType.STORY,
        status=WorkItemStatus.TODO,
        priority=1.0,
        created_at=datetime.utcnow(),
    )
    db.add(work_item)
    await db.commit()
    return work_item


@pytest.mark.asyncio
async def test_mark_work_item_as_done(
    db: AsyncSession, test_work_item: WorkItem, test_user_with_team_membership: User
):
    """Test marking a work item as done sets the completion date."""
    service = WorkItemService(db)

    # Verify initial state
    assert test_work_item.status != WorkItemStatus.DONE
    assert test_work_item.completed_at is None

    # Update to DONE status
    update_data = WorkItemUpdateRequest(status=WorkItemStatus.DONE)
    response = await service.update_work_item(
        test_work_item.id,
        update_data,
        test_user_with_team_membership.id,
    )

    # Verify response
    assert response.status == WorkItemStatus.DONE
    assert response.completed_at is not None

    # Verify database state
    result = await db.execute(select(WorkItem).where(WorkItem.id == test_work_item.id))
    updated_item = result.scalar_one()
    assert updated_item.status == WorkItemStatus.DONE
    assert updated_item.completed_at is not None


@pytest.mark.asyncio
async def test_move_work_item_from_done_clears_completion(
    db: AsyncSession, test_work_item: WorkItem, test_user_with_team_membership: User
):
    """Test moving a work item from done status clears the completion date."""
    service = WorkItemService(db)

    # First mark as done
    test_work_item.status = WorkItemStatus.DONE
    test_work_item.completed_at = datetime.utcnow()
    await db.commit()

    # Verify initial state
    assert test_work_item.status == WorkItemStatus.DONE
    assert test_work_item.completed_at is not None

    # Update to IN_PROGRESS status
    update_data = WorkItemUpdateRequest(status=WorkItemStatus.IN_PROGRESS)
    response = await service.update_work_item(
        test_work_item.id,
        update_data,
        test_user_with_team_membership.id,
    )

    # Verify response
    assert response.status == WorkItemStatus.IN_PROGRESS
    assert response.completed_at is None

    # Verify database state
    result = await db.execute(select(WorkItem).where(WorkItem.id == test_work_item.id))
    updated_item = result.scalar_one()
    assert updated_item.status == WorkItemStatus.IN_PROGRESS
    assert updated_item.completed_at is None


@pytest.mark.asyncio
async def test_update_done_work_item_preserves_completion(
    db: AsyncSession, test_work_item: WorkItem, test_user_with_team_membership: User
):
    """Test updating a done work item preserves completion date."""
    service = WorkItemService(db)

    # First mark as done
    original_completion = datetime.utcnow()
    test_work_item.status = WorkItemStatus.DONE
    test_work_item.completed_at = original_completion
    await db.commit()

    # Update title only
    update_data = WorkItemUpdateRequest(title="Updated Title")
    response = await service.update_work_item(
        test_work_item.id,
        update_data,
        test_user_with_team_membership.id,
    )

    # Verify response
    assert response.status == WorkItemStatus.DONE
    assert response.completed_at == original_completion

    # Verify database state
    result = await db.execute(select(WorkItem).where(WorkItem.id == test_work_item.id))
    updated_item = result.scalar_one()
    assert updated_item.status == WorkItemStatus.DONE
    assert updated_item.completed_at == original_completion


@pytest.mark.asyncio
async def test_completion_date_not_set_for_other_status_changes(
    db: AsyncSession, test_work_item: WorkItem, test_user_with_team_membership: User
):
    """Test completion date not set for non-done status changes."""
    service = WorkItemService(db)

    # Verify initial state
    assert test_work_item.status == WorkItemStatus.TODO
    assert test_work_item.completed_at is None

    # Update to IN_PROGRESS status
    update_data = WorkItemUpdateRequest(status=WorkItemStatus.IN_PROGRESS)
    response = await service.update_work_item(
        test_work_item.id,
        update_data,
        test_user_with_team_membership.id,
    )

    # Verify response
    assert response.status == WorkItemStatus.IN_PROGRESS
    assert response.completed_at is None

    # Verify database state
    result = await db.execute(select(WorkItem).where(WorkItem.id == test_work_item.id))
    updated_item = result.scalar_one()
    assert updated_item.status == WorkItemStatus.IN_PROGRESS
    assert updated_item.completed_at is None

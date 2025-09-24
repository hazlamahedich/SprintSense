from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from fastapi import HTTPException

from app.domains.services.sprint_assignment_service import SprintAssignmentService

pytestmark = pytest.mark.asyncio


@pytest.fixture
def db():
    class AsyncTransaction:
        async def __aenter__(self):
            return None

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class DummyDB:
        def __init__(self):
            self._fetch_one = AsyncMock()

        async def fetch_one(self, *args, **kwargs):
            return await self._fetch_one(*args, **kwargs)

        def transaction(self):
            return AsyncTransaction()

    dummy = DummyDB()
    # Expose fetch_one mock for test configuration convenience
    dummy.fetch_one = dummy._fetch_one
    return dummy


@pytest.fixture
def service(db):
    return SprintAssignmentService(db)


@pytest.fixture
def work_item_id():
    return UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def sprint_id():
    return UUID("87654321-8765-4321-8765-432187654321")


@pytest.fixture
def user_id():
    return UUID("11111111-1111-1111-1111-111111111111")


async def test_assign_work_item_to_sprint_success(
    service, db, work_item_id, sprint_id, user_id
):
    # Mock database responses
    db.fetch_one.side_effect = [
        {"version": 1, "sprint_id": None},  # Work item check
        {"status": "Future", "team_id": "team1"},  # Sprint check
        {"exists": True},  # Team membership check
        {"version": 2, "sprint_id": str(sprint_id)},  # Update result
    ]

    result = await service.assign_work_item_to_sprint(
        work_item_id=work_item_id,
        sprint_id=sprint_id,
        current_version=1,
        user_id=user_id,
    )

    assert result.work_item_id == work_item_id
    assert result.sprint_id == sprint_id
    assert result.version == 2


async def test_assign_work_item_to_sprint_wrong_version(
    service, db, work_item_id, sprint_id, user_id
):
    db.fetch_one.return_value = {"version": 2, "sprint_id": None}

    with pytest.raises(HTTPException) as exc_info:
        await service.assign_work_item_to_sprint(
            work_item_id=work_item_id,
            sprint_id=sprint_id,
            current_version=1,
            user_id=user_id,
        )

    assert exc_info.value.status_code == 409
    assert "modified by another user" in exc_info.value.detail


async def test_assign_work_item_to_sprint_non_future_sprint(
    service, db, work_item_id, sprint_id, user_id
):
    db.fetch_one.side_effect = [
        {"version": 1, "sprint_id": None},  # Work item check
        {"status": "Active", "team_id": "team1"},  # Sprint check
    ]

    with pytest.raises(HTTPException) as exc_info:
        await service.assign_work_item_to_sprint(
            work_item_id=work_item_id,
            sprint_id=sprint_id,
            current_version=1,
            user_id=user_id,
        )

    assert exc_info.value.status_code == 400
    assert "Can only assign to Future sprints" in exc_info.value.detail


async def test_assign_work_item_to_sprint_unauthorized(
    service, db, work_item_id, sprint_id, user_id
):
    db.fetch_one.side_effect = [
        {"version": 1, "sprint_id": None},  # Work item check
        {"status": "Future", "team_id": "team1"},  # Sprint check
        None,  # No team membership
    ]

    with pytest.raises(HTTPException) as exc_info:
        await service.assign_work_item_to_sprint(
            work_item_id=work_item_id,
            sprint_id=sprint_id,
            current_version=1,
            user_id=user_id,
        )

    assert exc_info.value.status_code == 403
    assert "Not authorized" in exc_info.value.detail


async def test_remove_work_item_from_sprint(service, db, work_item_id, user_id):
    db.fetch_one.side_effect = [
        {"version": 1, "sprint_id": "some-uuid"},  # Work item check
        {"version": 2, "sprint_id": None},  # Update result
    ]

    result = await service.assign_work_item_to_sprint(
        work_item_id=work_item_id, sprint_id=None, current_version=1, user_id=user_id
    )

    assert result.work_item_id == work_item_id
    assert result.sprint_id is None
    assert result.version == 2

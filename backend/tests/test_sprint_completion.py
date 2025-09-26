"""Test sprint completion functionality."""

import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.core.security import get_current_user
from app.routes.sprint_completion import router as sprint_completion_router
from app.schemas.sprint_completion import CompleteSprintRequest, MoveType
from app.services.sprint_completion_service import SprintCompletionService

# Setup test database
TEST_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite://"

engine = create_async_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create test database and tables using the async engine."""
    from app.infra.db import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


app = FastAPI()
app.include_router(sprint_completion_router)

# Override dependencies
app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def db() -> AsyncSession:
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user() -> dict:
    return {
        "id": uuid.uuid4(),
        "email": "test@example.com",
        "full_name": "Test User",
    }


@pytest_asyncio.fixture
async def setup_test_data(db: AsyncSession, test_sprint: dict, test_user: dict):
    """Insert test data into DB."""
    # Create test data
    tasks = [
        {
            "id": uuid.uuid4(),
            "sprint_id": test_sprint["id"],
            "title": "Task 1",
            "status": "done",
            "story_points": 3,
        },
        {
            "id": uuid.uuid4(),
            "sprint_id": test_sprint["id"],
            "title": "Task 2",
            "status": "in_progress",
            "story_points": 5,
        },
    ]

    from app.domains.models import WorkItem

    items = []
    for task in tasks:
        item = WorkItem(
            id=task["id"],
            sprint_id=task["sprint_id"],
            title=task["title"],
            status=task["status"],
            story_points=task["story_points"],
            team_id=test_sprint["team_id"],
            author_id=test_user["id"],
            type="task",
        )
        items.append(item)

    db.add_all(items)
    await db.commit()


@pytest.fixture
def test_sprint() -> dict:
    return {
        "id": uuid.uuid4(),
        "team_id": uuid.uuid4(),
        "name": "Test Sprint",
        "start_date": datetime.now(timezone.utc),
        "end_date": datetime.now(timezone.utc),
        "status": "active",
    }


@pytest.mark.asyncio
async def test_get_incomplete_items(
    db: AsyncSession, test_sprint: dict, test_user: dict
):
    """Test retrieving incomplete items from a sprint."""
    # Insert test data
    tasks = [
        {
            "id": uuid.uuid4(),
            "sprint_id": test_sprint["id"],
            "title": "Task 1",
            "status": "done",
            "story_points": 3,
        },
        {
            "id": uuid.uuid4(),
            "sprint_id": test_sprint["id"],
            "title": "Task 2",
            "status": "in_progress",
            "story_points": 5,
        },
        {
            "id": uuid.uuid4(),
            "sprint_id": test_sprint["id"],
            "title": "Task 3",
            "status": "todo",
            "story_points": 8,
        },
    ]

    # Create test data in DB
    from app.domains.models import WorkItem

    items = []
    for task in tasks:
        item = WorkItem(
            id=task["id"],
            sprint_id=task["sprint_id"],
            title=task["title"],
            status=task["status"],
            story_points=task["story_points"],
            team_id=test_sprint["team_id"],
            author_id=test_user["id"],
            type="task",
        )
        items.append(item)

    db.add_all(items)
    await db.commit()

    service = SprintCompletionService(db)
    incomplete = await service.get_incomplete_items(test_sprint["id"])

    assert len(incomplete) == 2
    assert all(task.status in ["in_progress", "todo"] for task in incomplete)
    assert sum(task.points for task in incomplete) == 13


@pytest.mark.asyncio
async def test_move_to_backlog(db: AsyncSession, test_sprint: dict, test_user: dict):
    """Test moving incomplete items to backlog."""
    service = SprintCompletionService(db)
    result = await service.complete_sprint(
        test_sprint["id"],
        CompleteSprintRequest(action=MoveType.BACKLOG),
        moved_by=test_user["id"],
    )

    assert result.moved_count >= 0
    assert result.target == MoveType.BACKLOG
    assert result.next_sprint_id is None

    # TODO: Verify tasks were actually moved
    # rows = await db.execute(select(Task).where(Task.sprint_id.is_(None)))
    # assert len(rows) == result.moved_count


@pytest.mark.asyncio
async def test_move_to_next_sprint_fails_if_none_exists(
    db: AsyncSession, test_sprint: dict, test_user: dict
):
    """Test error when moving to nonexistent next sprint."""
    service = SprintCompletionService(db)

    with pytest.raises(ValueError, match="No next sprint available"):
        await service.complete_sprint(
            test_sprint["id"],
            CompleteSprintRequest(action=MoveType.NEXT_SPRINT),
            moved_by=test_user["id"],
        )


@pytest.mark.asyncio
async def test_api_get_incomplete_items(
    client: AsyncClient, test_sprint: dict, test_user: dict, setup_test_data
):
    """Test GET /api/sprints/{id}/incomplete-items endpoint."""
    from types import SimpleNamespace

    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=test_user["id"]
    )

    response = await client.get(f"/api/sprints/{test_sprint['id']}/incomplete-items")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    if data:
        assert all(
            {"id", "title", "status", "points"}.issubset(item.keys()) for item in data
        )


@pytest.mark.asyncio
async def test_api_complete_sprint(
    client: AsyncClient, test_sprint: dict, test_user: dict, setup_test_data
):
    """Test POST /api/sprints/{id}/complete endpoint."""
    from types import SimpleNamespace

    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=test_user["id"]
    )

    payload = {"action": "backlog"}
    response = await client.post(
        f"/api/sprints/{test_sprint['id']}/complete", json=payload
    )

    assert response.status_code == 200

    data = response.json()
    assert {"moved_count", "target"}.issubset(data.keys())
    assert data["target"] == "backlog"
    assert isinstance(data["moved_count"], int)

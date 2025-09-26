"""Tests for the velocity service."""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.models.sprint import Sprint
from app.domains.models.task import Task
from app.services.velocity_service import VelocityService


@pytest.mark.asyncio
async def test_get_team_velocity_empty(db_session: AsyncSession):
    """Test getting velocity data for team with no sprints."""
    service = VelocityService(db_session)
    team_id = uuid4()

    velocity_data = await service.get_team_velocity(team_id)
    assert len(velocity_data) == 0


@pytest.mark.asyncio
async def test_get_team_velocity_with_data(db_session: AsyncSession):
    """Test getting velocity data for team with sprints."""
    service = VelocityService(db_session)
    team_id = uuid4()

    # Create test sprints
    sprints = []
    now = datetime.utcnow()
    for i in range(3):
        sprint = Sprint(
            id=uuid4(),
            team_id=team_id,
            name=f"Sprint {i+1}",
            status="closed",
            start_date=now - timedelta(days=(3 - i) * 14),
            end_date=now - timedelta(days=(2 - i) * 14),
            velocity_calculated=False,
        )
        sprints.append(sprint)
        db_session.add(sprint)

    # Create test tasks with story points
    points_per_sprint = [13, 21, 34]
    for sprint, points in zip(sprints, points_per_sprint):
        task = Task(
            id=uuid4(),
            sprint_id=sprint.id,
            title=f"Task for {sprint.name}",
            status="done",
            story_points=points,
        )
        db_session.add(task)

    await db_session.commit()

    # Get velocity data
    velocity_data = await service.get_team_velocity(team_id)

    # Verify data
    assert len(velocity_data) == 3
    for data, sprint, points in zip(velocity_data, sprints, points_per_sprint):
        assert data.sprint_id == str(sprint.id)
        assert data.sprint_name == sprint.name
        assert data.points == points
        assert data.start_date == sprint.start_date.isoformat()
        assert data.end_date == sprint.end_date.isoformat()


@pytest.mark.asyncio
async def test_get_team_velocity_limit(db_session: AsyncSession):
    """Test velocity data limit parameter."""
    service = VelocityService(db_session)
    team_id = uuid4()

    # Create 5 sprints
    now = datetime.utcnow()
    for i in range(5):
        sprint = Sprint(
            id=uuid4(),
            team_id=team_id,
            name=f"Sprint {i+1}",
            status="closed",
            start_date=now - timedelta(days=(5 - i) * 14),
            end_date=now - timedelta(days=(4 - i) * 14),
            velocity_calculated=False,
        )
        db_session.add(sprint)

        task = Task(
            id=uuid4(),
            sprint_id=sprint.id,
            title=f"Task for Sprint {i+1}",
            status="done",
            story_points=13,
        )
        db_session.add(task)

    await db_session.commit()

    # Get velocity data with limit=3
    velocity_data = await service.get_team_velocity(team_id, limit=3)
    assert len(velocity_data) == 3


@pytest.mark.asyncio
async def test_get_team_velocity_no_done_tasks(db_session: AsyncSession):
    """Test velocity calculation with no completed tasks."""
    service = VelocityService(db_session)
    team_id = uuid4()

    # Create sprint with no completed tasks
    sprint = Sprint(
        id=uuid4(),
        team_id=team_id,
        name="Sprint 1",
        status="closed",
        start_date=datetime.utcnow() - timedelta(days=14),
        end_date=datetime.utcnow(),
        velocity_calculated=False,
    )
    db_session.add(sprint)

    task = Task(
        id=uuid4(),
        sprint_id=sprint.id,
        title="Incomplete Task",
        status="in_progress",
        story_points=13,
    )
    db_session.add(task)

    await db_session.commit()

    velocity_data = await service.get_team_velocity(team_id)
    assert len(velocity_data) == 1
    assert velocity_data[0].points == 0

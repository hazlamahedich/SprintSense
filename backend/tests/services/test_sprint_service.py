"""Unit tests for sprint service."""

import uuid
from datetime import date
from unittest.mock import Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.models.sprint import Sprint
from app.domains.models.team import Team
from app.schemas.sprint import SprintCreate
from app.services.sprint_service import SprintService


@pytest.fixture
async def mock_session():
    """Create a mock database session."""
    session = Mock(spec=AsyncSession)
    session.execute = Mock()
    session.commit = Mock()
    session.refresh = Mock()
    return session


@pytest.fixture
def sprint_service():
    """Create a sprint service instance."""
    return SprintService()


@pytest.fixture
def team_id():
    """Create a test team ID."""
    return uuid.uuid4()


@pytest.fixture
def valid_sprint_data():
    """Create valid sprint creation data."""
    return SprintCreate(
        name="Test Sprint",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 15),
        goal="Test sprint goal",
    )


@pytest.mark.asyncio
async def test_create_sprint_validates_dates(
    mock_session, sprint_service, team_id, valid_sprint_data
):
    """Test that sprint creation validates dates."""
    # Test with invalid dates (end before start)
    invalid_data = SprintCreate(
        name="Invalid Sprint",
        start_date=date(2025, 1, 15),
        end_date=date(2025, 1, 1),
        goal="Invalid dates",
    )

    # Should raise value error
    with pytest.raises(ValueError) as exc:
        await sprint_service.create_sprint(mock_session, team_id, invalid_data)
    assert "end_date must be after start_date" in str(exc.value)

    # Test with valid dates
    mock_session.execute.return_value.scalar_one_or_none.return_value = None
    await sprint_service.create_sprint(mock_session, team_id, valid_sprint_data)

    # Verify session was called correctly
    assert mock_session.add.called
    assert mock_session.commit.called
    assert mock_session.refresh.called


@pytest.mark.asyncio
async def test_prevent_multiple_active_sprints(
    mock_session, sprint_service, team_id, valid_sprint_data
):
    """Test that only one sprint can be active at a time per team."""
    # Mock an existing active sprint
    active_sprint = Sprint(
        id=uuid.uuid4(),
        team_id=team_id,
        name="Active Sprint",
        status=SprintStatus.ACTIVE,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 15),
    )
    mock_session.execute.return_value.scalar_one_or_none.return_value = active_sprint

    # Try to activate another sprint
    with pytest.raises(HTTPException) as exc:
        await sprint_service.update_sprint_status(mock_session, uuid.uuid4(), "active")

    assert exc.value.status_code == 409
    assert "Another sprint is already active" in exc.value.detail


@pytest.mark.asyncio
async def test_valid_state_transitions(mock_session, sprint_service, team_id):
    """Test that valid state transitions are allowed."""
    # Create sprints in different states
    future_sprint = Sprint(
        id=uuid.uuid4(),
        team_id=team_id,
        name="Future Sprint",
        status="future",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 15),
    )

    active_sprint = Sprint(
        id=uuid.uuid4(),
        team_id=team_id,
        name="Active Sprint",
        status="active",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 15),
    )

    # Test future -> active transition
    mock_session.execute.return_value.scalar_one_or_none.return_value = future_sprint
    await sprint_service.update_sprint_status(mock_session, future_sprint.id, "active")
    assert future_sprint.status == "active"

    # Test active -> closed transition
    mock_session.execute.return_value.scalar_one_or_none.return_value = active_sprint
    await sprint_service.update_sprint_status(mock_session, active_sprint.id, "closed")
    assert active_sprint.status == "closed"


@pytest.mark.asyncio
async def test_invalid_state_transitions(mock_session, sprint_service, team_id):
    """Test that invalid state transitions are prevented."""
    # Create a sprint
    future_sprint = Sprint(
        id=uuid.uuid4(),
        team_id=team_id,
        name="Future Sprint",
        status="future",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 15),
    )

    closed_sprint = Sprint(
        id=uuid.uuid4(),
        team_id=team_id,
        name="Closed Sprint",
        status="closed",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 15),
    )

    # Test future -> closed (invalid)
    mock_session.execute.return_value.scalar_one_or_none.return_value = future_sprint
    with pytest.raises(HTTPException) as exc:
        await sprint_service.update_sprint_status(
            mock_session, future_sprint.id, "closed"
        )
    assert exc.value.status_code == 400
    assert "Invalid state transition" in exc.value.detail

    # Test closed -> active (invalid)
    mock_session.execute.return_value.scalar_one_or_none.return_value = closed_sprint
    with pytest.raises(HTTPException) as exc:
        await sprint_service.update_sprint_status(
            mock_session, closed_sprint.id, "active"
        )
    assert exc.value.status_code == 400
    assert "Invalid state transition" in exc.value.detail

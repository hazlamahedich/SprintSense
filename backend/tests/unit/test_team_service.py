"""Unit tests for TeamService."""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.models.team import Team, TeamMember, TeamRole
from app.domains.models.user import User
from app.domains.schemas.team import TeamCreateRequest
from app.domains.services.team_service import TeamService


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def team_service(mock_db_session):
    """Team service with mocked database session."""
    return TeamService(mock_db_session)


@pytest.fixture
def sample_user():
    """Sample user for testing."""
    return User(
        id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password",
        is_active=True,
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_team():
    """Sample team for testing."""
    return Team(
        id=uuid.uuid4(),
        name="Test Team",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def team_create_request():
    """Sample team creation request."""
    return TeamCreateRequest(name="New Team")


@pytest.mark.asyncio
async def test_check_team_name_exists_for_user_returns_false_when_no_team_exists(
    team_service, mock_db_session, sample_user
):
    """Test that check_team_name_exists_for_user returns False when no team exists."""
    # Arrange
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = None
    mock_db_session.execute.return_value = mock_result

    # Act
    result = await team_service.check_team_name_exists_for_user(
        "Test Team", sample_user.id
    )

    # Assert
    assert result is False
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_check_team_name_exists_for_user_returns_true_when_team_exists(
    team_service, mock_db_session, sample_user, sample_team
):
    """Test that check_team_name_exists_for_user returns True when team exists."""
    # Arrange
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = sample_team
    mock_db_session.execute.return_value = mock_result

    # Act
    result = await team_service.check_team_name_exists_for_user(
        "Test Team", sample_user.id
    )

    # Assert
    assert result is True
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_create_team_success(
    team_service, mock_db_session, sample_user, team_create_request
):
    """Test successful team creation."""
    # Arrange
    team_id = uuid.uuid4()

    # Mock check for existing team (returns False)
    mock_check_result = MagicMock()
    mock_check_result.scalars().first.return_value = None

    # Mock team retrieval after creation
    created_team = Team(
        id=team_id,
        name="New Team",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    created_team.members = [
        TeamMember(
            id=uuid.uuid4(),
            team_id=team_id,
            user_id=sample_user.id,
            role=TeamRole.OWNER,
            created_at=datetime.utcnow(),
        )
    ]

    mock_get_result = MagicMock()
    mock_get_result.scalars().first.return_value = created_team

    # Configure mock to return different results for different calls
    mock_db_session.execute.side_effect = [mock_check_result, mock_get_result]

    # Mock flush to simulate getting team ID
    async def mock_flush():
        # Simulate the team getting an ID after flush
        pass

    mock_db_session.flush = AsyncMock(side_effect=mock_flush)
    mock_db_session.add = MagicMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.refresh = AsyncMock()

    # Act
    result = await team_service.create_team(team_create_request, sample_user)

    # Assert
    assert result.name == "New Team"
    assert result.id == team_id
    assert len(result.members) == 1
    assert result.members[0].role == TeamRole.OWNER
    assert result.members[0].user_id == sample_user.id

    # Verify database operations
    assert mock_db_session.add.call_count == 2  # Team and TeamMember
    mock_db_session.flush.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_create_team_raises_error_when_name_exists(
    team_service, mock_db_session, sample_user, sample_team, team_create_request
):
    """Test that create_team raises ValueError when team name already exists."""
    # Arrange
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = sample_team
    mock_db_session.execute.return_value = mock_result

    # Act & Assert
    with pytest.raises(ValueError, match="Team with name 'New Team' already exists"):
        await team_service.create_team(team_create_request, sample_user)


@pytest.mark.asyncio
async def test_get_team_by_id(team_service, mock_db_session, sample_team):
    """Test getting team by ID."""
    # Arrange
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = sample_team
    mock_db_session.execute.return_value = mock_result

    # Act
    result = await team_service.get_team_by_id(sample_team.id)

    # Assert
    assert result == sample_team
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_teams_by_user(
    team_service, mock_db_session, sample_user, sample_team
):
    """Test getting teams by user."""
    # Arrange
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [sample_team]
    mock_db_session.execute.return_value = mock_result

    # Act
    result = await team_service.get_teams_by_user(sample_user.id)

    # Assert
    assert len(result) == 1
    assert result[0] == sample_team
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_is_user_team_owner_returns_true_when_owner(
    team_service, mock_db_session, sample_user, sample_team
):
    """Test that is_user_team_owner returns True when user is owner."""
    # Arrange
    team_member = TeamMember(
        id=uuid.uuid4(),
        team_id=sample_team.id,
        user_id=sample_user.id,
        role=TeamRole.OWNER,
        created_at=datetime.utcnow(),
    )

    mock_result = MagicMock()
    mock_result.scalars().first.return_value = team_member
    mock_db_session.execute.return_value = mock_result

    # Act
    result = await team_service.is_user_team_owner(sample_team.id, sample_user.id)

    # Assert
    assert result is True
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_is_user_team_owner_returns_false_when_not_owner(
    team_service, mock_db_session, sample_user, sample_team
):
    """Test that is_user_team_owner returns False when user is not owner."""
    # Arrange
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = None
    mock_db_session.execute.return_value = mock_result

    # Act
    result = await team_service.is_user_team_owner(sample_team.id, sample_user.id)

    # Assert
    assert result is False
    mock_db_session.execute.assert_called_once()


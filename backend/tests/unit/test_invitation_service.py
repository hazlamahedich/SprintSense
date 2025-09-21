"""Unit tests for InvitationService."""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.models.team import Invitation, InvitationStatus, TeamMember, TeamRole
from app.domains.models.user import User
from app.domains.schemas.invitation import InvitationCreateRequest
from app.domains.services.invitation_service import InvitationService


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def invitation_service(mock_db_session):
    """Invitation service with mocked database session."""
    return InvitationService(mock_db_session)


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
def sample_inviter():
    """Sample inviter user for testing."""
    return User(
        id=uuid.uuid4(),
        email="inviter@example.com",
        full_name="Inviter User",
        hashed_password="hashed_password",
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_invitation():
    """Sample invitation for testing."""
    return Invitation(
        id=uuid.uuid4(),
        team_id=uuid.uuid4(),
        email="invited@example.com",
        role=TeamRole.MEMBER,
        status=InvitationStatus.PENDING,
        inviter_id=uuid.uuid4(),
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def invitation_create_request():
    """Sample invitation creation request."""
    return InvitationCreateRequest(email="invited@example.com", role=TeamRole.MEMBER)


@pytest.mark.asyncio
async def test_check_user_is_team_member_returns_false_when_user_not_exists(
    invitation_service, mock_db_session
):
    """Test that check_user_is_team_member returns False when user doesn't exist."""
    # Arrange
    team_id = uuid.uuid4()
    email = "nonexistent@example.com"

    mock_result = MagicMock()
    mock_result.scalars().first.return_value = None
    mock_db_session.execute.return_value = mock_result

    # Act
    result = await invitation_service.check_user_is_team_member(team_id, email)

    # Assert
    assert result is False
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_check_user_is_team_member_returns_false_when_user_not_member(
    invitation_service, mock_db_session, sample_user
):
    """Test check_user_is_team_member returns False when user not member."""
    # Arrange
    team_id = uuid.uuid4()

    # Mock user exists
    mock_user_result = MagicMock()
    mock_user_result.scalars().first.return_value = sample_user

    # Mock user is not team member
    mock_member_result = MagicMock()
    mock_member_result.scalars().first.return_value = None

    mock_db_session.execute.side_effect = [mock_user_result, mock_member_result]

    # Act
    result = await invitation_service.check_user_is_team_member(
        team_id, sample_user.email
    )

    # Assert
    assert result is False
    assert mock_db_session.execute.call_count == 2


@pytest.mark.asyncio
async def test_check_user_is_team_member_returns_true_when_user_is_member(
    invitation_service, mock_db_session, sample_user
):
    """Test that check_user_is_team_member returns True when user is a team member."""
    # Arrange
    team_id = uuid.uuid4()
    team_member = TeamMember(
        id=uuid.uuid4(),
        team_id=team_id,
        user_id=sample_user.id,
        role=TeamRole.MEMBER,
        created_at=datetime.utcnow(),
    )

    # Mock user exists
    mock_user_result = MagicMock()
    mock_user_result.scalars().first.return_value = sample_user

    # Mock user is team member
    mock_member_result = MagicMock()
    mock_member_result.scalars().first.return_value = team_member

    mock_db_session.execute.side_effect = [mock_user_result, mock_member_result]

    # Act
    result = await invitation_service.check_user_is_team_member(
        team_id, sample_user.email
    )

    # Assert
    assert result is True
    assert mock_db_session.execute.call_count == 2


@pytest.mark.asyncio
async def test_check_invitation_exists_returns_false_when_no_invitation(
    invitation_service, mock_db_session
):
    """Test that check_invitation_exists returns False when no invitation exists."""
    # Arrange
    team_id = uuid.uuid4()
    email = "test@example.com"

    mock_result = MagicMock()
    mock_result.scalars().first.return_value = None
    mock_db_session.execute.return_value = mock_result

    # Act
    result = await invitation_service.check_invitation_exists(team_id, email)

    # Assert
    assert result is False
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_check_invitation_exists_returns_true_when_invitation_exists(
    invitation_service, mock_db_session, sample_invitation
):
    """Test that check_invitation_exists returns True when invitation exists."""
    # Arrange
    team_id = sample_invitation.team_id
    email = sample_invitation.email

    mock_result = MagicMock()
    mock_result.scalars().first.return_value = sample_invitation
    mock_db_session.execute.return_value = mock_result

    # Act
    result = await invitation_service.check_invitation_exists(team_id, email)

    # Assert
    assert result is True
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_create_invitation_success(
    invitation_service, mock_db_session, sample_inviter, invitation_create_request
):
    """Test successful invitation creation."""
    # Arrange
    team_id = uuid.uuid4()

    # Mock user is not team member
    mock_user_result = MagicMock()
    mock_user_result.scalars().first.return_value = None

    # Mock no existing invitation
    mock_invitation_result = MagicMock()
    mock_invitation_result.scalars().first.return_value = None

    mock_db_session.execute.side_effect = [mock_user_result, mock_invitation_result]
    mock_db_session.add = MagicMock()
    mock_db_session.commit = AsyncMock()

    # Mock refresh to set the ID and created_at on the invitation
    def mock_refresh(invitation):
        invitation.id = uuid.uuid4()
        invitation.created_at = datetime.utcnow()

    mock_db_session.refresh = AsyncMock(side_effect=mock_refresh)

    # Act
    result = await invitation_service.create_invitation(
        team_id, invitation_create_request, sample_inviter
    )

    # Assert
    assert result.email == invitation_create_request.email.lower()
    assert result.role == invitation_create_request.role
    assert result.status == InvitationStatus.PENDING
    assert result.inviter_id == sample_inviter.id
    assert result.team_id == team_id

    # Verify database operations
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_create_invitation_raises_error_when_user_already_member(
    invitation_service,
    mock_db_session,
    sample_user,
    sample_inviter,
    invitation_create_request,
):
    """Test create_invitation raises ValueError when user already member."""
    # Arrange
    team_id = uuid.uuid4()
    team_member = TeamMember(
        id=uuid.uuid4(),
        team_id=team_id,
        user_id=sample_user.id,
        role=TeamRole.MEMBER,
        created_at=datetime.utcnow(),
    )

    # Mock user exists and is team member
    mock_user_result = MagicMock()
    mock_user_result.scalars().first.return_value = sample_user

    mock_member_result = MagicMock()
    mock_member_result.scalars().first.return_value = team_member

    mock_db_session.execute.side_effect = [mock_user_result, mock_member_result]

    # Act & Assert
    with pytest.raises(ValueError, match="This user is already a member of this team"):
        await invitation_service.create_invitation(
            team_id, invitation_create_request, sample_inviter
        )


@pytest.mark.asyncio
async def test_create_invitation_raises_error_when_invitation_exists(
    invitation_service,
    mock_db_session,
    sample_invitation,
    sample_inviter,
    invitation_create_request,
):
    """Test that create_invitation raises ValueError when invitation already exists."""
    # Arrange
    team_id = sample_invitation.team_id

    # Mock user is not team member
    mock_user_result = MagicMock()
    mock_user_result.scalars().first.return_value = None

    # Mock invitation already exists
    mock_invitation_result = MagicMock()
    mock_invitation_result.scalars().first.return_value = sample_invitation

    mock_db_session.execute.side_effect = [mock_user_result, mock_invitation_result]

    # Act & Assert
    with pytest.raises(
        ValueError, match="An invitation has already been sent to this email"
    ):
        await invitation_service.create_invitation(
            team_id, invitation_create_request, sample_inviter
        )


@pytest.mark.asyncio
async def test_get_team_invitations(
    invitation_service, mock_db_session, sample_invitation, sample_inviter
):
    """Test getting team invitations with inviter names."""
    # Arrange
    team_id = sample_invitation.team_id

    # Mock query result with invitation and inviter name
    mock_result = MagicMock()
    mock_result.__iter__.return_value = [(sample_invitation, sample_inviter.full_name)]
    mock_db_session.execute.return_value = mock_result

    # Act
    result = await invitation_service.get_team_invitations(team_id)

    # Assert
    assert len(result) == 1
    invitation_item = result[0]
    assert invitation_item.id == sample_invitation.id
    assert invitation_item.email == sample_invitation.email
    assert invitation_item.role == sample_invitation.role
    assert invitation_item.status == sample_invitation.status
    assert invitation_item.inviter_name == sample_inviter.full_name
    assert invitation_item.created_at == sample_invitation.created_at

    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_invitation_by_id(
    invitation_service, mock_db_session, sample_invitation
):
    """Test getting invitation by ID."""
    # Arrange
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = sample_invitation
    mock_db_session.execute.return_value = mock_result

    # Act
    result = await invitation_service.get_invitation_by_id(sample_invitation.id)

    # Assert
    assert result == sample_invitation
    mock_db_session.execute.assert_called_once()

"""Unit tests for invitation endpoints."""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from starlette import status

from app.api.v1.endpoints.teams import create_invitation, list_team_invitations
from app.domains.models.team import InvitationStatus, TeamRole
from app.domains.models.user import User
from app.domains.schemas.invitation import (
    InvitationCreateRequest,
    InvitationListItem,
    InvitationResponse,
)
from app.domains.services.invitation_service import InvitationService
from app.domains.services.team_service import TeamService


@pytest.fixture
def mock_invitation_service():
    """Mock invitation service."""
    return AsyncMock(spec=InvitationService)


@pytest.fixture
def mock_team_service():
    """Mock team service."""
    return AsyncMock(spec=TeamService)


@pytest.fixture
def current_user():
    """Mock current user."""
    return User(
        id=uuid.uuid4(),
        email="owner@example.com",
        full_name="Team Owner",
        hashed_password="hashed_password",
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def invitation_create_request():
    """Sample invitation creation request."""
    return InvitationCreateRequest(email="invited@example.com", role=TeamRole.MEMBER)


@pytest.fixture
def invitation_response():
    """Sample invitation response."""
    return InvitationResponse(
        id=uuid.uuid4(),
        team_id=uuid.uuid4(),
        email="invited@example.com",
        role=TeamRole.MEMBER,
        status=InvitationStatus.PENDING,
        inviter_id=uuid.uuid4(),
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def invitation_list_items():
    """Sample invitation list items."""
    return [
        InvitationListItem(
            id=uuid.uuid4(),
            email="user1@example.com",
            role=TeamRole.MEMBER,
            status=InvitationStatus.PENDING,
            inviter_name="Team Owner",
            created_at=datetime.utcnow(),
        ),
        InvitationListItem(
            id=uuid.uuid4(),
            email="user2@example.com",
            role=TeamRole.OWNER,
            status=InvitationStatus.PENDING,
            inviter_name="Team Owner",
            created_at=datetime.utcnow(),
        ),
    ]


@pytest.mark.asyncio
async def test_create_team_invitation_success(
    mock_invitation_service,
    mock_team_service,
    current_user,
    invitation_create_request,
    invitation_response,
):
    """Test successful team invitation creation."""
    # Arrange
    team_id = uuid.uuid4()
    mock_team_service.is_user_team_owner.return_value = True
    mock_invitation_service.create_invitation.return_value = invitation_response

    # Act
    result = await create_invitation(
        team_id=str(team_id),
        invitation_data=invitation_create_request,
        current_user=current_user,
        invitation_service=mock_invitation_service,
        team_service=mock_team_service,
    )

    # Assert
    assert result.message == "Invitation sent successfully"
    assert result.invitation == invitation_response
    mock_team_service.is_user_team_owner.assert_called_once_with(
        uuid.UUID(str(team_id)), current_user.id
    )
    mock_invitation_service.create_invitation.assert_called_once_with(
        uuid.UUID(str(team_id)), invitation_create_request, current_user
    )


@pytest.mark.asyncio
async def test_create_team_invitation_not_owner(
    mock_invitation_service,
    mock_team_service,
    current_user,
    invitation_create_request,
):
    """Test team invitation creation fails when user is not owner."""
    # Arrange
    team_id = uuid.uuid4()
    mock_team_service.is_user_team_owner.return_value = False

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await create_invitation(
            team_id=str(team_id),
            invitation_data=invitation_create_request,
            current_user=current_user,
            invitation_service=mock_invitation_service,
            team_service=mock_team_service,
        )

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Only team owners can send invitations" in str(exc_info.value.detail)
    mock_team_service.is_user_team_owner.assert_called_once_with(
        uuid.UUID(str(team_id)), current_user.id
    )
    mock_invitation_service.create_invitation.assert_not_called()


@pytest.mark.asyncio
async def test_create_team_invitation_service_error(
    mock_invitation_service,
    mock_team_service,
    current_user,
    invitation_create_request,
):
    """Test team invitation creation handles service errors."""
    # Arrange
    team_id = uuid.uuid4()
    mock_team_service.is_user_team_owner.return_value = True
    mock_invitation_service.create_invitation.side_effect = ValueError(
        "This user is already a member of this team"
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await create_invitation(
            team_id=str(team_id),
            invitation_data=invitation_create_request,
            current_user=current_user,
            invitation_service=mock_invitation_service,
            team_service=mock_team_service,
        )

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "This user is already a member of this team"


@pytest.mark.asyncio
async def test_list_team_invitations_success(
    mock_invitation_service,
    mock_team_service,
    current_user,
    invitation_list_items,
):
    """Test successful team invitations listing."""
    # Arrange
    team_id = uuid.uuid4()
    mock_team_service.is_user_team_owner.return_value = True
    mock_invitation_service.get_team_invitations.return_value = invitation_list_items

    # Act
    result = await list_team_invitations(
        team_id=str(team_id),
        current_user=current_user,
        invitation_service=mock_invitation_service,
        team_service=mock_team_service,
    )

    # Assert
    assert result.invitations == invitation_list_items
    mock_team_service.is_user_team_owner.assert_called_once_with(
        uuid.UUID(str(team_id)), current_user.id
    )
    mock_invitation_service.get_team_invitations.assert_called_once_with(
        uuid.UUID(str(team_id))
    )


@pytest.mark.asyncio
async def test_list_team_invitations_not_owner(
    mock_invitation_service,
    mock_team_service,
    current_user,
):
    """Test team invitations listing fails when user is not owner."""
    # Arrange
    team_id = uuid.uuid4()
    mock_team_service.is_user_team_owner.return_value = False

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await list_team_invitations(
            team_id=str(team_id),
            current_user=current_user,
            invitation_service=mock_invitation_service,
            team_service=mock_team_service,
        )

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Only team owners can view invitations" in str(exc_info.value.detail)
    mock_team_service.is_user_team_owner.assert_called_once_with(
        uuid.UUID(str(team_id)), current_user.id
    )
    mock_invitation_service.get_team_invitations.assert_not_called()


@pytest.mark.asyncio
async def test_list_team_invitations_empty_list(
    mock_invitation_service,
    mock_team_service,
    current_user,
):
    """Test team invitations listing returns empty list when no invitations."""
    # Arrange
    team_id = uuid.uuid4()
    mock_team_service.is_user_team_owner.return_value = True
    mock_invitation_service.get_team_invitations.return_value = []

    # Act
    result = await list_team_invitations(
        team_id=str(team_id),
        current_user=current_user,
        invitation_service=mock_invitation_service,
        team_service=mock_team_service,
    )

    # Assert
    assert result.invitations == []
    mock_team_service.is_user_team_owner.assert_called_once_with(
        uuid.UUID(str(team_id)), current_user.id
    )
    mock_invitation_service.get_team_invitations.assert_called_once_with(
        uuid.UUID(str(team_id))
    )


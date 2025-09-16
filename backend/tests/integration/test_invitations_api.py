"""Integration tests for invitation API endpoints."""

import uuid

import pytest
from fastapi import status
from httpx import AsyncClient

from app.domains.models.team import (
    Invitation,
    InvitationStatus,
    Team,
    TeamMember,
    TeamRole,
)
from app.domains.models.user import User


@pytest.mark.asyncio
async def test_create_invitation_success(
    authenticated_async_client: AsyncClient,
    authenticated_user: User,
    user_team: Team,
    db_session,
):
    """Test successful invitation creation."""
    # Create invitation data
    invitation_data = {"email": "newuser@example.com", "role": "member"}

    # Make request
    response = await authenticated_async_client.post(
        f"/api/v1/teams/{user_team.id}/invitations", json=invitation_data
    )

    # Assert response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["message"] == "Invitation sent successfully"
    assert data["invitation"]["email"] == "newuser@example.com"
    assert data["invitation"]["role"] == "member"
    assert data["invitation"]["status"] == "pending"
    assert data["invitation"]["team_id"] == str(user_team.id)
    assert data["invitation"]["inviter_id"] == str(authenticated_user.id)

    # Verify database record was created using ORM
    from sqlalchemy import and_, select

    result = await db_session.execute(
        select(Invitation).where(
            and_(
                Invitation.team_id == user_team.id,
                Invitation.email == "newuser@example.com",
            )
        )
    )
    invitation_record = result.scalars().first()
    assert invitation_record is not None
    assert invitation_record.status == InvitationStatus.PENDING
    assert invitation_record.role == TeamRole.MEMBER


@pytest.mark.asyncio
async def test_create_invitation_not_team_owner(
    async_client: AsyncClient, other_user: User, user_team: Team
):
    """Test invitation creation fails when user is not team owner."""
    from datetime import timedelta

    from app.core.security import create_access_token

    # Create access token for other user (not team owner)
    access_token = create_access_token(
        data={"sub": str(other_user.id), "email": other_user.email},
        expires_delta=timedelta(minutes=30),
    )

    invitation_data = {"email": "newuser@example.com", "role": "member"}

    response = await async_client.post(
        f"/api/v1/teams/{user_team.id}/invitations",
        json=invitation_data,
        cookies={"access_token": access_token},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Only team owners can send invitations" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_invitation_user_already_member(
    authenticated_async_client: AsyncClient,
    authenticated_user: User,
    other_user: User,
    user_team: Team,
    db_session,
):
    """Test invitation creation fails when user is already team member."""
    # Add other_user as team member
    team_member = TeamMember(
        team_id=user_team.id, user_id=other_user.id, role=TeamRole.MEMBER
    )
    db_session.add(team_member)
    await db_session.commit()

    invitation_data = {"email": other_user.email, "role": "member"}

    response = await authenticated_async_client.post(
        f"/api/v1/teams/{user_team.id}/invitations", json=invitation_data
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "already a member of this team" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_invitation_duplicate(
    authenticated_async_client: AsyncClient,
    authenticated_user: User,
    user_team: Team,
    db_session,
):
    """Test invitation creation fails when invitation already exists."""
    # Create existing invitation
    existing_invitation = Invitation(
        team_id=user_team.id,
        email="existing@example.com",
        role=TeamRole.MEMBER,
        status=InvitationStatus.PENDING,
        inviter_id=authenticated_user.id,
    )
    db_session.add(existing_invitation)
    await db_session.commit()

    invitation_data = {"email": "existing@example.com", "role": "member"}

    response = await authenticated_async_client.post(
        f"/api/v1/teams/{user_team.id}/invitations", json=invitation_data
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "already been sent to this email" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_invitation_invalid_email(
    authenticated_async_client: AsyncClient, authenticated_user: User, user_team: Team
):
    """Test invitation creation fails with invalid email."""
    invitation_data = {"email": "invalid-email", "role": "member"}

    response = await authenticated_async_client.post(
        f"/api/v1/teams/{user_team.id}/invitations", json=invitation_data
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_create_invitation_missing_email(
    authenticated_async_client: AsyncClient, authenticated_user: User, user_team: Team
):
    """Test invitation creation fails with missing email."""
    invitation_data = {"role": "member"}

    response = await authenticated_async_client.post(
        f"/api/v1/teams/{user_team.id}/invitations", json=invitation_data
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_list_invitations_success(
    authenticated_async_client: AsyncClient,
    authenticated_user: User,
    user_team: Team,
    db_session,
):
    """Test successful listing of team invitations."""
    # Create test invitations
    invitation1 = Invitation(
        team_id=user_team.id,
        email="user1@example.com",
        role=TeamRole.MEMBER,
        status=InvitationStatus.PENDING,
        inviter_id=authenticated_user.id,
    )
    invitation2 = Invitation(
        team_id=user_team.id,
        email="user2@example.com",
        role=TeamRole.OWNER,
        status=InvitationStatus.PENDING,
        inviter_id=authenticated_user.id,
    )
    db_session.add_all([invitation1, invitation2])
    await db_session.commit()
    await db_session.refresh(invitation1)
    await db_session.refresh(invitation2)

    response = await authenticated_async_client.get(
        f"/api/v1/teams/{user_team.id}/invitations"
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "invitations" in data
    assert len(data["invitations"]) == 2

    # Check invitation details
    invitations = data["invitations"]
    emails = [inv["email"] for inv in invitations]
    assert "user1@example.com" in emails
    assert "user2@example.com" in emails

    # Check that inviter_name is populated
    for invitation in invitations:
        assert "inviter_name" in invitation
        assert invitation["inviter_name"] == authenticated_user.full_name
        assert invitation["status"] == "pending"


@pytest.mark.asyncio
async def test_list_invitations_empty(
    authenticated_async_client: AsyncClient, authenticated_user: User, user_team: Team
):
    """Test listing invitations when none exist."""
    response = await authenticated_async_client.get(
        f"/api/v1/teams/{user_team.id}/invitations"
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["invitations"] == []


@pytest.mark.asyncio
async def test_list_invitations_not_team_owner(
    async_client: AsyncClient, other_user: User, user_team: Team
):
    """Test listing invitations fails when user is not team owner."""
    from datetime import timedelta

    from app.core.security import create_access_token

    # Create access token for other user (not team owner)
    access_token = create_access_token(
        data={"sub": str(other_user.id), "email": other_user.email},
        expires_delta=timedelta(minutes=30),
    )

    response = await async_client.get(
        f"/api/v1/teams/{user_team.id}/invitations",
        cookies={"access_token": access_token},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Only team owners can view invitations" in response.json()["detail"]


@pytest.mark.asyncio
async def test_invitation_endpoints_unauthenticated(
    async_client: AsyncClient, user_team: Team
):
    """Test invitation endpoints require authentication."""
    # Test create invitation without authentication
    invitation_data = {"email": "test@example.com", "role": "member"}
    response = await async_client.post(
        f"/api/v1/teams/{user_team.id}/invitations", json=invitation_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Test list invitations without authentication
    response = await async_client.get(f"/api/v1/teams/{user_team.id}/invitations")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_invitation_nonexistent_team(
    authenticated_async_client: AsyncClient, authenticated_user: User
):
    """Test invitation endpoints with nonexistent team."""
    nonexistent_team_id = uuid.uuid4()

    invitation_data = {"email": "test@example.com", "role": "member"}

    response = await authenticated_async_client.post(
        f"/api/v1/teams/{nonexistent_team_id}/invitations", json=invitation_data
    )

    # User is not owner of nonexistent team, so should get 403
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_invitation_invalid_team_id(
    authenticated_async_client: AsyncClient, authenticated_user: User
):
    """Test invitation endpoints with invalid team ID format."""
    invalid_team_id = "not-a-uuid"

    invitation_data = {"email": "test@example.com", "role": "member"}

    response = await authenticated_async_client.post(
        f"/api/v1/teams/{invalid_team_id}/invitations", json=invitation_data
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

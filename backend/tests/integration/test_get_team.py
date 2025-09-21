"""Tests for team retrieval endpoint."""

import uuid
from http import HTTPStatus

import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.domains.models.team import Team, TeamMember, TeamRole
from app.domains.models.user import User


@pytest.mark.asyncio
async def test_get_team_by_id_success(
    async_client: AsyncClient,
    test_user: User,
    test_db_session,
    auth_headers: dict,
):
    """Test successful team retrieval."""
    # Create test team
    team = Team(name="Test Team")
    test_db_session.add(team)
    await test_db_session.flush()

    # Add test user as member
    member = TeamMember(team_id=team.id, user_id=test_user.id, role=TeamRole.OWNER)
    test_db_session.add(member)
    await test_db_session.commit()

    # Get team
    response = await async_client.get(
        f"{settings.API_V1_PREFIX}/teams/{team.id}",
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["id"] == str(team.id)
    assert data["name"] == "Test Team"
    assert len(data["members"]) == 1
    assert data["members"][0]["user_id"] == str(test_user.id)
    assert data["members"][0]["role"] == TeamRole.OWNER.value


@pytest.mark.asyncio
async def test_get_team_not_found(async_client: AsyncClient, auth_headers: dict):
    """Test team retrieval with non-existent ID."""
    response = await async_client.get(
        f"{settings.API_V1_PREFIX}/teams/{uuid.uuid4()}",
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    data = response.json()
    assert data["code"] == "TEAM_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_team_unauthorized(async_client: AsyncClient):
    """Test team retrieval without authentication."""
    response = await async_client.get(
        f"{settings.API_V1_PREFIX}/teams/{uuid.uuid4()}",
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_team_forbidden(
    async_client: AsyncClient,
    test_user: User,
    other_user: User,
    test_db_session,
    auth_headers: dict,
):
    """Test team retrieval by non-member."""
    # Create test team with other_user as member
    team = Team(name="Other Team")
    test_db_session.add(team)
    await test_db_session.flush()

    member = TeamMember(team_id=team.id, user_id=other_user.id, role=TeamRole.OWNER)
    test_db_session.add(member)
    await test_db_session.commit()

    # Try to get team as test_user (non-member)
    response = await async_client.get(
        f"{settings.API_V1_PREFIX}/teams/{team.id}",
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    data = response.json()
    assert data["code"] == "NOT_TEAM_MEMBER"

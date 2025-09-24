"""Integration tests for teams API endpoints."""

from typing import Dict

import pytest
from httpx import AsyncClient

from app.domains.models.user import User


class TestTeamsAPI:
    """Test class for teams API endpoints."""

    @pytest.mark.asyncio
    async def test_create_team_success(
        self,
        test_user: User,
        auth_headers_for_user: Dict[str, str],
        async_client: AsyncClient,
    ):
        """Test successful team creation."""
        team_data = {"name": "My Test Team"}

        response = await async_client.post(
            "/api/v1/teams/", json=team_data, headers=auth_headers_for_user
        )

        assert response.status_code == 201

        data = response.json()
        assert data["message"] == "Team created successfully"
        assert data["team"]["name"] == "My Test Team"
        assert data["team"]["id"] is not None
        assert len(data["team"]["members"]) == 1
        assert data["team"]["members"][0]["user_id"] == str(test_user.id)
        assert data["team"]["members"][0]["role"] == "owner"

    @pytest.mark.asyncio
    async def test_create_team_duplicate_name_fails(
        self,
        test_user: User,
        auth_headers_for_user: Dict[str, str],
        async_client: AsyncClient,
    ):
        """Test that creating a team with duplicate name fails."""
        team_data = {"name": "Duplicate Team"}

        # Create first team
        response1 = await async_client.post(
            "/api/v1/teams/", json=team_data, headers=auth_headers_for_user
        )
        assert response1.status_code == 201

        # Try to create second team with same name
        response2 = await async_client.post(
            "/api/v1/teams/", json=team_data, headers=auth_headers_for_user
        )

        assert response2.status_code == 409
        data = response2.json()
        assert data["detail"]["code"] == "TEAM_NAME_EXISTS"
        assert "already exists" in data["detail"]["message"]

    @pytest.mark.asyncio
    async def test_create_team_validates_name_length(
        self,
        test_user: User,
        auth_headers_for_user: Dict[str, str],
        async_client: AsyncClient,
    ):
        """Test that team name validation works."""
        # Test empty name
        response1 = await async_client.post(
            "/api/v1/teams/", json={"name": ""}, headers=auth_headers_for_user
        )
        assert response1.status_code == 422

        # Test name too long
        long_name = "a" * 101  # 101 characters, max is 100
        response2 = await async_client.post(
            "/api/v1/teams/", json={"name": long_name}, headers=auth_headers_for_user
        )
        assert response2.status_code == 422

    @pytest.mark.asyncio
    async def test_create_team_requires_authentication(self, async_client: AsyncClient):
        """Test that team creation requires authentication."""
        team_data = {"name": "Test Team"}

        response = await async_client.post("/api/v1/teams/", json=team_data)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_team_trims_whitespace(
        self,
        test_user: User,
        auth_headers_for_user: Dict[str, str],
        async_client: AsyncClient,
    ):
        """Test that team name whitespace is trimmed."""
        team_data = {"name": "  Whitespace Team  "}

        response = await async_client.post(
            "/api/v1/teams/", json=team_data, headers=auth_headers_for_user
        )

        assert response.status_code == 201
        data = response.json()
        assert data["team"]["name"] == "Whitespace Team"

    @pytest.mark.asyncio
    async def test_create_team_handles_invalid_json(
        self,
        test_user: User,
        auth_headers_for_user: Dict[str, str],
        async_client: AsyncClient,
    ):
        """Test that invalid JSON is handled properly."""
        response = await async_client.post(
            "/api/v1/teams/",
            content="invalid json",
            headers={**auth_headers_for_user, "Content-Type": "application/json"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_team_handles_missing_name_field(
        self,
        test_user: User,
        auth_headers_for_user: Dict[str, str],
        async_client: AsyncClient,
    ):
        """Test that missing name field is handled properly."""
        response = await async_client.post(
            "/api/v1/teams/",
            json={},  # Missing name field
            headers=auth_headers_for_user,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_team_success(
        self,
        test_user: User,
        auth_headers_for_user: Dict[str, str],
        async_client: AsyncClient,
    ):
        """Test successful team retrieval."""
        # First create a team
        team_data = {"name": "Test Team For Retrieval"}
        create_response = await async_client.post(
            "/api/v1/teams/", json=team_data, headers=auth_headers_for_user
        )

        assert create_response.status_code == 201
        team_id = create_response.json()["team"]["id"]

        # Now try to retrieve it
        get_response = await async_client.get(
            f"/api/v1/teams/{team_id}", headers=auth_headers_for_user
        )

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["name"] == "Test Team For Retrieval"
        assert data["id"] == team_id
        assert len(data["members"]) == 1
        assert data["members"][0]["user_id"] == str(test_user.id)
        assert data["members"][0]["role"] == "owner"

    @pytest.mark.asyncio
    async def test_get_team_not_found(
        self,
        auth_headers_for_user: Dict[str, str],
        async_client: AsyncClient,
    ):
        """Test 404 response for non-existent team."""
        non_existent_id = "12345678-1234-5678-1234-567812345678"
        response = await async_client.get(
            f"/api/v1/teams/{non_existent_id}", headers=auth_headers_for_user
        )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["code"] == "TEAM_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_get_team_unauthorized_access(
        self,
        test_user: User,
        other_test_user: User,  # Another user who is not a team member
        auth_headers_for_user: Dict[str, str],
        auth_headers_for_other_user: Dict[str, str],
        async_client: AsyncClient,
    ):
        """Test 403 response when non-member tries to access team."""
        # Create team as first user
        team_data = {"name": "Restricted Team"}
        create_response = await async_client.post(
            "/api/v1/teams/", json=team_data, headers=auth_headers_for_user
        )

        assert create_response.status_code == 201
        team_id = create_response.json()["team"]["id"]

        # Try to access as other user
        get_response = await async_client.get(
            f"/api/v1/teams/{team_id}", headers=auth_headers_for_other_user
        )

        assert get_response.status_code == 403
        data = get_response.json()
        assert data["detail"]["code"] == "NOT_TEAM_MEMBER"

    @pytest.mark.asyncio
    async def test_get_team_no_auth(
        self,
        test_user: User,
        auth_headers_for_user: Dict[str, str],
        async_client: AsyncClient,
    ):
        """Test 401 response when no authentication provided."""
        # First create a team
        team_data = {"name": "Auth Required Team"}
        create_response = await async_client.post(
            "/api/v1/teams/", json=team_data, headers=auth_headers_for_user
        )

        assert create_response.status_code == 201
        team_id = create_response.json()["team"]["id"]

        # Try to access without auth headers
        get_response = await async_client.get(f"/api/v1/teams/{team_id}")

        assert get_response.status_code == 401

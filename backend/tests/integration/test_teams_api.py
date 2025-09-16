"""Integration tests for teams API endpoints."""

from typing import Dict

import pytest
from httpx import AsyncClient

from app.domains.models.user import User


class TestTeamsAPI:
    """Test class for teams API endpoints."""

    @pytest.mark.asyncio
    async def test_create_team_success(
        self, test_user: User, auth_headers_for_user: Dict[str, str], async_client: AsyncClient
    ):
        """Test successful team creation."""
        team_data = {"name": "My Test Team"}
        
        response = await async_client.post(
            "/api/v1/teams/",
            json=team_data,
            headers=auth_headers_for_user
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
        self, test_user: User, auth_headers_for_user: Dict[str, str], async_client: AsyncClient
    ):
        """Test that creating a team with duplicate name fails."""
        team_data = {"name": "Duplicate Team"}
        
        # Create first team
        response1 = await async_client.post(
            "/api/v1/teams/",
            json=team_data,
            headers=auth_headers_for_user
        )
        assert response1.status_code == 201
        
        # Try to create second team with same name
        response2 = await async_client.post(
            "/api/v1/teams/",
            json=team_data,
            headers=auth_headers_for_user
        )
        
        assert response2.status_code == 409
        data = response2.json()
        assert "already exists" in data["detail"]

    @pytest.mark.asyncio
    async def test_create_team_validates_name_length(
        self, test_user: User, auth_headers_for_user: Dict[str, str], async_client: AsyncClient
    ):
        """Test that team name validation works."""
        # Test empty name
        response1 = await async_client.post(
            "/api/v1/teams/",
            json={"name": ""},
            headers=auth_headers_for_user
        )
        assert response1.status_code == 422
        
        # Test name too long
        long_name = "a" * 101  # 101 characters, max is 100
        response2 = await async_client.post(
            "/api/v1/teams/",
            json={"name": long_name},
            headers=auth_headers_for_user
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
        self, test_user: User, auth_headers_for_user: Dict[str, str], async_client: AsyncClient
    ):
        """Test that team name whitespace is trimmed."""
        team_data = {"name": "  Whitespace Team  "}
        
        response = await async_client.post(
            "/api/v1/teams/",
            json=team_data,
            headers=auth_headers_for_user
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["team"]["name"] == "Whitespace Team"

    @pytest.mark.asyncio
    async def test_create_team_handles_invalid_json(
        self, test_user: User, auth_headers_for_user: Dict[str, str], async_client: AsyncClient
    ):
        """Test that invalid JSON is handled properly."""
        response = await async_client.post(
            "/api/v1/teams/",
            content="invalid json",
            headers={**auth_headers_for_user, "Content-Type": "application/json"}
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio 
    async def test_create_team_handles_missing_name_field(
        self, test_user: User, auth_headers_for_user: Dict[str, str], async_client: AsyncClient
    ):
        """Test that missing name field is handled properly."""
        response = await async_client.post(
            "/api/v1/teams/",
            json={},  # Missing name field
            headers=auth_headers_for_user
        )
        
        assert response.status_code == 422

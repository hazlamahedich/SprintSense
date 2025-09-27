"""Tests for authentication functionality."""

import uuid
from datetime import timedelta

import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.security import create_access_token
from app.domains.models.user import User


@pytest.fixture
def test_token(test_user: User) -> str:
    """Create a valid test token."""
    return create_access_token(
        subject=str(test_user.id),
        expires_delta=timedelta(minutes=30),
        email=test_user.email
    )


@pytest.mark.asyncio
async def test_cookie_auth_success(
    async_client: AsyncClient, test_user: User, test_token: str
):
    """Test successful authentication using cookie."""
    response = await async_client.get(
        "/api/v1/users/me",
        cookies={"access_token": test_token},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_header_auth_success(
    async_client: AsyncClient, test_user: User, test_token: str
):
    """Test successful authentication using Authorization header."""
    response = await async_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_no_auth_fails(async_client: AsyncClient):
    """Test request without authentication fails."""
    response = await async_client.get("/api/v1/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_invalid_token_fails(async_client: AsyncClient):
    """Test authentication with invalid token fails."""
    invalid_token = "invalid.token.here"

    # Test with cookie
    response = await async_client.get(
        "/api/v1/users/me",
        cookies={"access_token": invalid_token},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Test with header
    response = await async_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_expired_token_fails(async_client: AsyncClient, test_user: User):
    """Test authentication with expired token fails."""
    expired_token = create_access_token(
        subject=str(test_user.id),
        expires_delta=timedelta(minutes=-30),
        email=test_user.email
    )

    # Test with cookie
    response = await async_client.get(
        "/api/v1/users/me",
        cookies={"access_token": expired_token},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Test with header
    response = await async_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_malformed_bearer_token_fails(async_client: AsyncClient):
    """Test authentication with malformed bearer token fails."""
    response = await async_client.get(
        "/api/v1/users/me",
        headers={"Authorization": "NotBearer token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = await async_client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer"},  # Missing token part
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_invalid_user_id_in_token(async_client: AsyncClient):
    """Test authentication with non-existent user ID fails."""
    non_existent_id = str(uuid.uuid4())
    token = create_access_token(
        subject=non_existent_id,
        expires_delta=timedelta(minutes=30),
        email="fake@example.com"
    )

    # Test with cookie
    response = await async_client.get(
        "/api/v1/users/me",
        cookies={"access_token": token},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Test with header
    response = await async_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

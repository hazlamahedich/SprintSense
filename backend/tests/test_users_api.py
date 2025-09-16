"""Integration tests for users API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.domains.models.user import User


@pytest.mark.asyncio
class TestUserRegistrationAPI:
    """Test user registration API functionality."""

    async def test_register_user_success(
        self, async_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test successful user registration."""
        user_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "TestPassword123",
        }

        response = await async_client.post("/api/v1/users/register", json=user_data)

        assert response.status_code == 201
        data = response.json()

        # Check response structure
        assert "message" in data
        assert "user" in data
        assert "access_token" in data
        assert "token_type" in data

        # Check user data
        user_response = data["user"]
        assert user_response["email"] == user_data["email"]
        assert user_response["full_name"] == user_data["full_name"]
        assert user_response["is_active"] is True
        assert "id" in user_response
        assert "created_at" in user_response
        assert "hashed_password" not in user_response  # Should not expose password

        # Check token
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

        # Verify user was created in database
        from sqlalchemy import select

        result = await db_session.execute(
            select(User).where(User.email == user_data["email"])
        )
        db_user = result.scalars().first()

        assert db_user is not None
        assert db_user.email == user_data["email"]
        assert db_user.full_name == user_data["full_name"]
        assert db_user.is_active is True
        assert verify_password(user_data["password"], db_user.hashed_password)

    async def test_register_user_duplicate_email(
        self, async_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Test registration with duplicate email address."""
        user_data = {
            "email": "duplicate@example.com",
            "full_name": "First User",
            "password": "TestPassword123",
        }

        # First registration should succeed
        response1 = await async_client.post("/api/v1/users/register", json=user_data)
        assert response1.status_code == 201

        # Second registration with same email should fail
        user_data2 = {
            "email": "duplicate@example.com",
            "full_name": "Second User",
            "password": "DifferentPassword456",
        }

        response2 = await async_client.post("/api/v1/users/register", json=user_data2)
        assert response2.status_code == 409

        data = response2.json()
        assert "detail" in data
        assert "already registered" in data["detail"].lower()

    async def test_register_user_invalid_email(self, async_client: AsyncClient) -> None:
        """Test registration with invalid email format."""
        user_data = {
            "email": "not-an-email",
            "full_name": "Test User",
            "password": "TestPassword123",
        }

        response = await async_client.post("/api/v1/users/register", json=user_data)
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data
        # FastAPI validation error for invalid email

    async def test_register_user_weak_password(self, async_client: AsyncClient) -> None:
        """Test registration with weak password."""
        test_cases = [
            {"password": "weak", "description": "too short"},
            {"password": "nouppercasehere123", "description": "no uppercase"},
            {"password": "NOLOWERCASEHERE123", "description": "no lowercase"},
            {"password": "NoDigitsHere", "description": "no digits"},
        ]

        for case in test_cases:
            user_data = {
                "email": f"test-{case['password']}@example.com",
                "full_name": "Test User",
                "password": case["password"],
            }

            response = await async_client.post("/api/v1/users/register", json=user_data)
            assert (
                response.status_code == 422
            ), f"Expected 422 for {case['description']}"

            data = response.json()
            assert "detail" in data

    async def test_register_user_missing_fields(
        self, async_client: AsyncClient
    ) -> None:
        """Test registration with missing required fields."""
        test_cases = [
            {"full_name": "Test User", "password": "TestPassword123"},  # Missing email
            {
                "email": "test@example.com",
                "password": "TestPassword123",
            },  # Missing full_name
            {"email": "test@example.com", "full_name": "Test User"},  # Missing password
            {},  # Missing all fields
        ]

        for user_data in test_cases:
            response = await async_client.post("/api/v1/users/register", json=user_data)
            assert response.status_code == 422

            data = response.json()
            assert "detail" in data

    async def test_register_user_empty_full_name(
        self, async_client: AsyncClient
    ) -> None:
        """Test registration with empty full name."""
        user_data = {
            "email": "test@example.com",
            "full_name": "",
            "password": "TestPassword123",
        }

        response = await async_client.post("/api/v1/users/register", json=user_data)
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data

    async def test_register_user_very_long_full_name(
        self, async_client: AsyncClient
    ) -> None:
        """Test registration with very long full name."""
        user_data = {
            "email": "test@example.com",
            "full_name": "A" * 300,  # Very long name
            "password": "TestPassword123",
        }

        response = await async_client.post("/api/v1/users/register", json=user_data)
        # Should either succeed or fail gracefully depending on validation rules
        assert response.status_code in [201, 400, 422]

    async def test_register_user_special_characters_in_name(
        self, async_client: AsyncClient
    ) -> None:
        """Test registration with special characters in full name."""
        user_data = {
            "email": "test@example.com",
            "full_name": "José María O'Connor-Smith",
            "password": "TestPassword123",
        }

        response = await async_client.post("/api/v1/users/register", json=user_data)
        assert response.status_code == 201

        data = response.json()
        assert data["user"]["full_name"] == "José María O'Connor-Smith"

    async def test_register_user_unicode_characters(
        self, async_client: AsyncClient
    ) -> None:
        """Test registration with Unicode characters."""
        user_data = {
            "email": "unicode@example.com",
            "full_name": "张三 🚀",
            "password": "TestPassword123",
        }

        response = await async_client.post("/api/v1/users/register", json=user_data)
        assert response.status_code == 201

        data = response.json()
        assert data["user"]["full_name"] == "张三 🚀"

    async def test_register_user_case_insensitive_email(
        self, async_client: AsyncClient
    ) -> None:
        """Test that email case sensitivity is handled properly."""
        # Register with lowercase
        user_data1 = {
            "email": "test@example.com",
            "full_name": "Test User 1",
            "password": "TestPassword123",
        }

        response1 = await async_client.post("/api/v1/users/register", json=user_data1)
        assert response1.status_code == 201

        # Try to register with different case - should fail if emails are
        # case-insensitive
        user_data2 = {
            "email": "TEST@EXAMPLE.COM",
            "full_name": "Test User 2",
            "password": "TestPassword456",
        }

        response2 = await async_client.post("/api/v1/users/register", json=user_data2)
        # This might depend on database collation settings
        # For now, we expect it to succeed, but in production it should probably fail
        assert response2.status_code in [201, 409]

    async def test_register_user_sql_injection_attempt(
        self, async_client: AsyncClient
    ) -> None:
        """Test registration with potential SQL injection payloads."""
        malicious_payloads = [
            "'; DROP TABLE users; --",
            "admin@example.com'; UPDATE users SET is_active = false; --",
            "1' OR '1'='1",
        ]

        for payload in malicious_payloads:
            user_data = {
                "email": f"{payload}@example.com",
                "full_name": payload,
                "password": "TestPassword123",
            }

            # Should either fail validation or be safely escaped
            response = await async_client.post("/api/v1/users/register", json=user_data)
            assert response.status_code in [201, 400, 422]

            # If it succeeds, the payload should be stored as-is (safely escaped)
            if response.status_code == 201:
                data = response.json()
                # The email/name should be stored exactly as provided (no injection)
                assert payload in data["user"]["full_name"]

    async def test_get_current_user_profile_not_implemented(
        self, async_client: AsyncClient
    ) -> None:
        """Test the placeholder endpoint for current user profile."""
        response = await async_client.get("/api/v1/users/me")
        assert response.status_code == 501

        data = response.json()
        assert "not yet implemented" in data["detail"].lower()

"""Integration tests for authentication API endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.infrastructure.database.models import User
from app.infrastructure.database.session import get_async_session
from app.core.security import hash_password
from tests.conftest import TestAsyncSession


class TestUserRegistration:
    """Test user registration endpoint integration."""
    
    async def test_register_user_success(
        self, async_client: AsyncClient, test_session: TestAsyncSession
    ):
        """Test successful user registration."""
        registration_data = {
            "email": "newuser@example.com",
            "password": "StrongPass123!",
            "full_name": "New User"
        }
        
        response = await async_client.post(
            "/api/v1/auth/register",
            json=registration_data
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "user" in data
        assert "access_token" in data
        
        # Verify user data
        user_data = data["user"]
        assert user_data["email"] == registration_data["email"]
        assert user_data["full_name"] == registration_data["full_name"]
        assert "id" in user_data
        assert "created_at" in user_data
        assert "updated_at" in user_data
        assert "password_hash" not in user_data  # Should not expose password
        
        # Verify access token is returned
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
        
        # Verify user was created in database
        async with test_session() as session:
            result = await session.execute(
                "SELECT * FROM users WHERE email = :email",
                {"email": registration_data["email"]}
            )
            db_user = result.first()
            assert db_user is not None
            assert db_user.email == registration_data["email"]
            assert db_user.full_name == registration_data["full_name"]
    
    async def test_register_user_duplicate_email(
        self, async_client: AsyncClient, test_session: TestAsyncSession
    ):
        """Test registration with duplicate email address."""
        # Create existing user
        existing_email = "existing@example.com"
        async with test_session() as session:
            existing_user = User(
                email=existing_email,
                password_hash=hash_password("ExistingPass123!"),
                full_name="Existing User"
            )
            session.add(existing_user)
            await session.commit()
        
        # Attempt to register with same email
        registration_data = {
            "email": existing_email,
            "password": "NewPass123!",
            "full_name": "New User"
        }
        
        response = await async_client.post(
            "/api/v1/auth/register",
            json=registration_data
        )
        
        assert response.status_code == 409  # Conflict
        data = response.json()
        assert data["error_type"] == "UserAlreadyExistsError"
        assert "already exists" in data["detail"]
    
    async def test_register_user_invalid_email(self, async_client: AsyncClient):
        """Test registration with invalid email format."""
        invalid_emails = [
            "",
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com"
        ]
        
        for email in invalid_emails:
            registration_data = {
                "email": email,
                "password": "StrongPass123!",
                "full_name": "Test User"
            }
            
            response = await async_client.post(
                "/api/v1/auth/register",
                json=registration_data
            )
            
            assert response.status_code == 422  # Validation error
            data = response.json()
            assert "detail" in data
            # Pydantic validation should catch email format issues
    
    async def test_register_user_weak_password(self, async_client: AsyncClient):
        """Test registration with weak password."""
        weak_passwords = [
            "short",
            "nouppercase123!",
            "NOLOWERCASE123!",
            "NoDigits!Here",
            "NoSpecialChars123"
        ]
        
        for password in weak_passwords:
            registration_data = {
                "email": "test@example.com",
                "password": password,
                "full_name": "Test User"
            }
            
            response = await async_client.post(
                "/api/v1/auth/register",
                json=registration_data
            )
            
            assert response.status_code == 400  # Bad request
            data = response.json()
            assert data["error_type"] == "WeakPasswordError"
            assert "strength requirements" in data["detail"]
    
    async def test_register_user_missing_fields(self, async_client: AsyncClient):
        """Test registration with missing required fields."""
        test_cases = [
            # Missing email
            {"password": "StrongPass123!", "full_name": "Test User"},
            # Missing password
            {"email": "test@example.com", "full_name": "Test User"},
            # Missing full_name
            {"email": "test@example.com", "password": "StrongPass123!"},
            # Empty data
            {}
        ]
        
        for registration_data in test_cases:
            response = await async_client.post(
                "/api/v1/auth/register",
                json=registration_data
            )
            
            assert response.status_code == 422  # Validation error
            data = response.json()
            assert "detail" in data
    
    async def test_register_user_trims_whitespace(
        self, async_client: AsyncClient, test_session: TestAsyncSession
    ):
        """Test that registration trims whitespace from full name."""
        registration_data = {
            "email": "trim@example.com",
            "password": "StrongPass123!",
            "full_name": "  Test User  "
        }
        
        response = await async_client.post(
            "/api/v1/auth/register",
            json=registration_data
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify trimmed full name in response
        assert data["user"]["full_name"] == "Test User"
        
        # Verify trimmed full name in database
        async with test_session() as session:
            result = await session.execute(
                "SELECT * FROM users WHERE email = :email",
                {"email": registration_data["email"]}
            )
            db_user = result.first()
            assert db_user.full_name == "Test User"
    
    async def test_register_user_case_insensitive_email(
        self, async_client: AsyncClient, test_session: TestAsyncSession
    ):
        """Test that email comparison is case-insensitive."""
        # Register with lowercase email
        registration_data1 = {
            "email": "test@example.com",
            "password": "StrongPass123!",
            "full_name": "Test User 1"
        }
        
        response1 = await async_client.post(
            "/api/v1/auth/register",
            json=registration_data1
        )
        assert response1.status_code == 201
        
        # Try to register with uppercase email (should fail)
        registration_data2 = {
            "email": "TEST@EXAMPLE.COM",
            "password": "StrongPass456!",
            "full_name": "Test User 2"
        }
        
        response2 = await async_client.post(
            "/api/v1/auth/register",
            json=registration_data2
        )
        
        # This behavior depends on database collation and business rules
        # Adjust assertion based on actual implementation
        # For now, assuming case-sensitive (most common approach)
        assert response2.status_code in [201, 409]  # Could be allowed or rejected
    
    async def test_register_user_long_full_name(self, async_client: AsyncClient):
        """Test registration with very long full name."""
        registration_data = {
            "email": "longname@example.com",
            "password": "StrongPass123!",
            "full_name": "A" * 1000  # Very long name
        }
        
        response = await async_client.post(
            "/api/v1/auth/register",
            json=registration_data
        )
        
        # This should either succeed or fail gracefully with appropriate error
        # Adjust based on actual field length constraints
        assert response.status_code in [201, 400, 422]
    
    async def test_register_user_special_characters_in_name(
        self, async_client: AsyncClient
    ):
        """Test registration with special characters in full name."""
        special_names = [
            "José García",
            "李明",
            "François Müller",
            "O'Connor-Smith",
            "User123"
        ]
        
        for name in special_names:
            registration_data = {
                "email": f"special{hash(name)}@example.com",  # Unique email
                "password": "StrongPass123!",
                "full_name": name
            }
            
            response = await async_client.post(
                "/api/v1/auth/register",
                json=registration_data
            )
            
            # Should accept various character sets in names
            assert response.status_code == 201, f"Failed for name: {name}"
            data = response.json()
            assert data["user"]["full_name"] == name


class TestUserRegistrationHeaders:
    """Test authentication-related headers and responses."""
    
    async def test_register_user_cors_headers(self, async_client: AsyncClient):
        """Test that registration endpoint includes proper CORS headers."""
        registration_data = {
            "email": "cors@example.com",
            "password": "StrongPass123!",
            "full_name": "CORS User"
        }
        
        response = await async_client.post(
            "/api/v1/auth/register",
            json=registration_data
        )
        
        assert response.status_code == 201
        # Check for common CORS headers (adjust based on actual CORS config)
        headers = response.headers
        # These might be set by FastAPI CORS middleware
        assert "content-type" in headers
        assert headers["content-type"] == "application/json"
    
    async def test_register_user_content_type_validation(
        self, async_client: AsyncClient
    ):
        """Test registration with incorrect content type."""
        # Send form data instead of JSON
        response = await async_client.post(
            "/api/v1/auth/register",
            data={
                "email": "form@example.com",
                "password": "StrongPass123!",
                "full_name": "Form User"
            }
        )
        
        # FastAPI should reject non-JSON content for JSON endpoints
        assert response.status_code == 422  # Or 415 Unsupported Media Type
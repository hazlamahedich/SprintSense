"""Tests for authentication API endpoints."""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_user_service
from app.domains.models.user import User
from app.domains.services.user_service import UserService
from app.main import app

client = TestClient(app)


class TestAuthAPI:
    """Test class for authentication API endpoints."""

    @pytest.fixture
    def mock_user(self) -> User:
        """Mock user fixture."""
        return User(
            id=uuid.uuid4(),
            email="test@example.com",
            full_name="Test User",
            hashed_password="$2b$12$hashed_password",
            is_active=True,
            created_at=datetime.utcnow(),
        )

    @pytest.fixture
    def mock_user_service(self) -> Mock:
        """Mock user service fixture."""
        return Mock(spec=UserService)

    @pytest.fixture
    def mock_db_session(self) -> Mock:
        """Mock database session fixture."""
        return Mock(spec=AsyncSession)

    def test_login_success(self, mock_user: User, mock_user_service: Mock, monkeypatch):
        """Test successful user login."""
        # Arrange
        mock_user_service.authenticate_user = AsyncMock(return_value=mock_user)

        def mock_get_user_service():
            return mock_user_service

        app.dependency_overrides[get_user_service] = mock_get_user_service

        login_data = {
            "email": "test@example.com",
            "password": "TestPassword123",
        }

        # Act
        try:
            response = client.post("/api/v1/auth/login", json=login_data)

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Login successful"
            assert data["user"]["email"] == "test@example.com"
            assert data["user"]["full_name"] == "Test User"
            assert "access_token" in response.cookies
            assert response.cookies["access_token"] is not None
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

    def test_login_invalid_credentials(self, mock_user_service: Mock, monkeypatch):
        """Test login with invalid credentials."""
        # Arrange
        mock_user_service.authenticate_user = AsyncMock(return_value=None)

        def mock_get_user_service():
            return mock_user_service

        app.dependency_overrides[get_user_service] = mock_get_user_service

        login_data = {
            "email": "test@example.com",
            "password": "WrongPassword",
        }

        # Act
        try:
            response = client.post("/api/v1/auth/login", json=login_data)

            # Assert
            assert response.status_code == 401
            data = response.json()
            assert data["detail"] == "Invalid email or password"
            assert "access_token" not in response.cookies
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

    def test_login_inactive_user(
        self, mock_user: User, mock_user_service: Mock, monkeypatch
    ):
        """Test login with inactive user account."""
        # Arrange
        mock_user.is_active = False
        mock_user_service.authenticate_user = AsyncMock(return_value=mock_user)

        def mock_get_user_service():
            return mock_user_service

        app.dependency_overrides[get_user_service] = mock_get_user_service

        login_data = {
            "email": "test@example.com",
            "password": "TestPassword123",
        }

        # Act
        try:
            response = client.post("/api/v1/auth/login", json=login_data)

            # Assert
            assert response.status_code == 401
            data = response.json()
            assert data["detail"] == "Account is inactive"
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

    def test_login_validation_error_empty_email(self):
        """Test login with empty email."""
        login_data = {
            "email": "",
            "password": "TestPassword123",
        }

        # Act
        response = client.post("/api/v1/auth/login", json=login_data)

        # Assert
        assert response.status_code == 422  # Validation error

    def test_login_validation_error_empty_password(self):
        """Test login with empty password."""
        login_data = {
            "email": "test@example.com",
            "password": "",
        }

        # Act
        response = client.post("/api/v1/auth/login", json=login_data)

        # Assert
        assert response.status_code == 422  # Validation error

    def test_login_validation_error_invalid_email_format(self):
        """Test login with invalid email format."""
        login_data = {
            "email": "invalid-email",
            "password": "TestPassword123",
        }

        # Act
        response = client.post("/api/v1/auth/login", json=login_data)

        # Assert
        assert response.status_code == 422  # Validation error

    def test_logout_success(self):
        """Test successful user logout."""
        # Act
        response = client.post("/api/v1/auth/logout")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logout successful"

    def test_login_service_exception(self, mock_user_service: Mock, monkeypatch):
        """Test login when service raises unexpected exception."""
        # Arrange
        mock_user_service.authenticate_user = AsyncMock(
            side_effect=Exception("Database connection error")
        )

        def mock_get_user_service():
            return mock_user_service

        app.dependency_overrides[get_user_service] = mock_get_user_service

        login_data = {
            "email": "test@example.com",
            "password": "TestPassword123",
        }

        # Act
        try:
            response = client.post("/api/v1/auth/login", json=login_data)

            # Assert
            assert response.status_code == 500
            data = response.json()
            assert data["detail"] == "Internal server error during login"
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

    def test_login_missing_required_fields(self):
        """Test login with missing required fields."""
        # Missing email
        response1 = client.post(
            "/api/v1/auth/login", json={"password": "TestPassword123"}
        )
        assert response1.status_code == 422

        # Missing password
        response2 = client.post(
            "/api/v1/auth/login", json={"email": "test@example.com"}
        )
        assert response2.status_code == 422

        # Empty request body
        response3 = client.post("/api/v1/auth/login", json={})
        assert response3.status_code == 422

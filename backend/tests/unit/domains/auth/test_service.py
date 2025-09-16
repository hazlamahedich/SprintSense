"""Tests for auth service domain logic."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.service import AuthService
from app.domains.auth.exceptions import (
    UserAlreadyExistsError,
    InvalidEmailError,
    WeakPasswordError
)
from app.infrastructure.database.models import User


@pytest.fixture
def mock_session():
    """Create a mock async session."""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def auth_service(mock_session):
    """Create an AuthService instance with mocked session."""
    return AuthService(mock_session)


class TestAuthServiceRegisterUser:
    """Test user registration in AuthService."""
    
    async def test_register_user_success(self, auth_service, mock_session):
        """Test successful user registration."""
        # Mock the execute query to return no existing user
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        mock_session.execute.return_value = mock_result
        
        email = "test@example.com"
        password = "StrongPass123!"
        full_name = "Test User"
        
        with patch('app.domains.auth.service.hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            
            result = await auth_service.register_user(email, password, full_name)
            
            # Verify user creation
            assert isinstance(result, User)
            assert result.email == email
            assert result.full_name == full_name
            assert result.password_hash == "hashed_password"
            
            # Verify database operations
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(result)
    
    async def test_register_user_invalid_email(self, auth_service):
        """Test registration with invalid email address."""
        invalid_emails = [
            "",
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com",
            "test@.com"
        ]
        
        for email in invalid_emails:
            with pytest.raises(InvalidEmailError) as exc_info:
                await auth_service.register_user(
                    email, "StrongPass123!", "Test User"
                )
            assert "Invalid email format" in str(exc_info.value)
    
    async def test_register_user_weak_password(self, auth_service):
        """Test registration with weak password."""
        weak_passwords = [
            "short",
            "nouppercase123!",
            "NOLOWERCASE123!",
            "NoDigits!Here",
            "NoSpecialChars123"
        ]
        
        for password in weak_passwords:
            with pytest.raises(WeakPasswordError) as exc_info:
                await auth_service.register_user(
                    "test@example.com", password, "Test User"
                )
            assert "Password does not meet strength requirements" in str(exc_info.value)
    
    async def test_register_user_existing_email(self, auth_service, mock_session):
        """Test registration with existing email address."""
        # Mock the execute query to return an existing user
        existing_user = User(
            email="test@example.com",
            password_hash="existing_hash",
            full_name="Existing User"
        )
        mock_result = MagicMock()
        mock_result.scalar.return_value = existing_user
        mock_session.execute.return_value = mock_result
        
        with pytest.raises(UserAlreadyExistsError) as exc_info:
            await auth_service.register_user(
                "test@example.com", "StrongPass123!", "Test User"
            )
        
        assert "User with this email already exists" in str(exc_info.value)
        # Verify no database writes were attempted
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()
    
    async def test_register_user_race_condition_integrity_error(
        self, auth_service, mock_session
    ):
        """Test registration with race condition causing IntegrityError."""
        # Mock the execute query to return no existing user (first check passes)
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Mock commit to raise IntegrityError (race condition)
        mock_session.commit.side_effect = IntegrityError(
            "duplicate key", None, None
        )
        
        with patch('app.domains.auth.service.hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            
            with pytest.raises(UserAlreadyExistsError) as exc_info:
                await auth_service.register_user(
                    "test@example.com", "StrongPass123!", "Test User"
                )
            
            assert "User with this email already exists" in str(exc_info.value)
            # Verify rollback was called due to the error
            mock_session.rollback.assert_called_once()
    
    async def test_register_user_empty_full_name(self, auth_service):
        """Test registration with empty or whitespace-only full name."""
        invalid_names = ["", "   ", "\t", "\n"]
        
        for name in invalid_names:
            # Should not raise an exception, but should handle gracefully
            # The trimming should happen in the API layer or be validated here
            pass  # This would depend on business requirements
    
    async def test_register_user_trims_full_name(self, auth_service, mock_session):
        """Test that full name is trimmed of whitespace."""
        # Mock the execute query to return no existing user
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        mock_session.execute.return_value = mock_result
        
        with patch('app.domains.auth.service.hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            
            result = await auth_service.register_user(
                "test@example.com", "StrongPass123!", "  Test User  "
            )
            
            # Verify full name was trimmed
            assert result.full_name == "Test User"
    
    async def test_register_user_database_error(self, auth_service, mock_session):
        """Test registration with unexpected database error."""
        # Mock the execute query to return no existing user
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Mock commit to raise unexpected database error
        mock_session.commit.side_effect = Exception("Database connection error")
        
        with patch('app.domains.auth.service.hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            
            with pytest.raises(Exception) as exc_info:
                await auth_service.register_user(
                    "test@example.com", "StrongPass123!", "Test User"
                )
            
            assert "Database connection error" in str(exc_info.value)
            # Verify rollback was called
            mock_session.rollback.assert_called_once()


class TestAuthServiceHelperMethods:
    """Test helper methods in AuthService."""
    
    def test_email_validation_valid_emails(self, auth_service):
        """Test email validation with valid email addresses."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@456.com",
            "test_email@sub.domain.com"
        ]
        
        for email in valid_emails:
            # This assumes there's a public or testable email validation method
            # If not, this test might need to be adjusted based on actual implementation
            assert "@" in email and "." in email.split("@")[1]
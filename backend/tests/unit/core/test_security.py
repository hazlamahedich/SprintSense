"""Tests for password security utilities."""
import pytest
from app.core.security import (
    hash_password,
    verify_password,
    is_password_strong,
    create_access_token,
    verify_access_token
)


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_hash_password_creates_hash(self):
        """Test that password hashing creates a hash."""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_hash_password_unique_salts(self):
        """Test that each password hash uses a unique salt."""
        password = "same_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2
    
    def test_verify_password_correct_password(self):
        """Test password verification with correct password."""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect_password(self):
        """Test password verification with incorrect password."""
        password = "test_password_123"
        wrong_password = "wrong_password_456"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty_password(self):
        """Test password verification with empty password."""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert verify_password("", hashed) is False
    
    def test_verify_password_invalid_hash(self):
        """Test password verification with invalid hash format."""
        password = "test_password_123"
        invalid_hash = "invalid_hash_format"
        
        assert verify_password(password, invalid_hash) is False


class TestPasswordStrength:
    """Test password strength validation."""
    
    def test_strong_password_valid(self):
        """Test that strong passwords are accepted."""
        strong_passwords = [
            "MyStr0ng!Pass",
            "Complex123@Password",
            "Secure$Pass9",
            "Long&Complex123Password"
        ]
        
        for password in strong_passwords:
            assert is_password_strong(password) is True, f"Failed for password: {password}"
    
    def test_weak_password_too_short(self):
        """Test that passwords shorter than 8 characters are rejected."""
        short_passwords = [
            "Sh0rt!",
            "1234567",
            "Ab1@",
            ""
        ]
        
        for password in short_passwords:
            assert is_password_strong(password) is False, f"Failed for password: {password}"
    
    def test_weak_password_no_uppercase(self):
        """Test that passwords without uppercase letters are rejected."""
        no_uppercase = [
            "lowercase123!",
            "all_lower_case@123",
            "simple123@password"
        ]
        
        for password in no_uppercase:
            assert is_password_strong(password) is False, f"Failed for password: {password}"
    
    def test_weak_password_no_lowercase(self):
        """Test that passwords without lowercase letters are rejected."""
        no_lowercase = [
            "UPPERCASE123!",
            "ALL_UPPER_CASE@123",
            "SIMPLE123@PASSWORD"
        ]
        
        for password in no_lowercase:
            assert is_password_strong(password) is False, f"Failed for password: {password}"
    
    def test_weak_password_no_digit(self):
        """Test that passwords without digits are rejected."""
        no_digits = [
            "NoDigits!Here",
            "Password@Without",
            "OnlyLetters&Special!"
        ]
        
        for password in no_digits:
            assert is_password_strong(password) is False, f"Failed for password: {password}"
    
    def test_weak_password_no_special_char(self):
        """Test that passwords without special characters are rejected."""
        no_special = [
            "NoSpecialChars123",
            "OnlyAlphaNumeric456",
            "Simple123Password"
        ]
        
        for password in no_special:
            assert is_password_strong(password) is False, f"Failed for password: {password}"


class TestJWTTokens:
    """Test JWT token creation and verification."""
    
    def test_create_access_token(self):
        """Test JWT token creation."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token = create_access_token(data={"user_id": user_id})
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert "." in token  # JWT tokens contain dots
    
    def test_verify_access_token_valid(self):
        """Test verification of valid JWT token."""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        token = create_access_token(data={"user_id": user_id})
        
        payload = verify_access_token(token)
        assert payload is not None
        assert payload["user_id"] == user_id
        assert "exp" in payload  # Should have expiration
    
    def test_verify_access_token_invalid(self):
        """Test verification of invalid JWT token."""
        invalid_tokens = [
            "invalid.jwt.token",
            "completely_invalid_token",
            "",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        ]
        
        for token in invalid_tokens:
            payload = verify_access_token(token)
            assert payload is None, f"Failed for token: {token}"
    
    def test_verify_access_token_expired(self):
        """Test verification of expired JWT token."""
        from datetime import timedelta
        
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        # Create token that expires immediately (negative timedelta)
        token = create_access_token(
            data={"user_id": user_id}, 
            expires_delta=timedelta(seconds=-1)
        )
        
        payload = verify_access_token(token)
        assert payload is None  # Expired token should return None
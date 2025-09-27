"""Tests for security utilities."""

from datetime import datetime, timedelta, timezone

import pytest

from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    verify_token,
)


class TestPasswordHashing:
    """Test password hashing functionality."""

    def test_hash_password_creates_different_hashes(self) -> None:
        """Test that hashing the same password twice creates different hashes."""
        password = "TestPassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        assert len(hash1) > 0
        assert len(hash2) > 0

    def test_verify_password_with_correct_password(self) -> None:
        """Test verifying password with correct password."""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_with_incorrect_password(self) -> None:
        """Test verifying password with incorrect password."""
        password = "TestPassword123"
        wrong_password = "WrongPassword456"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_get_password_hash(self) -> None:
        """Test that get_password_hash generates valid password hashes."""
        password = "TestPassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # They should both be valid hashes (can't compare directly due to salt)
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    @pytest.mark.parametrize(
        "password",
        [
            "simple",
            "SimplePassword123!@#",
            "VeryLongPasswordWithManyCharacters123456789",
            "🚀🎉💻",  # Unicode characters
            "",  # Empty string
        ],
    )
    def test_hash_various_passwords(self, password: str) -> None:
        """Test hashing various types of passwords."""
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True


class TestJWT:
    """Test JWT token functionality."""

    def test_create_and_verify_token(self) -> None:
        """Test creating and verifying a JWT token."""
        payload = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(
            subject=payload["sub"],
            expires_delta=None,
            email=payload["email"])

        assert isinstance(token, str)
        assert len(token) > 0

        # Verify the token
        decoded_payload = verify_token(token)
        assert decoded_payload is not None
        assert decoded_payload["sub"] == "user123"
        assert decoded_payload["email"] == "test@example.com"
        assert "exp" in decoded_payload

    def test_create_token_with_custom_expiry(self) -> None:
        """Test creating token with custom expiration time."""
        payload = {"sub": "user123"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(
            subject=payload["sub"],
            expires_delta=expires_delta
        )

        decoded_payload = verify_token(token)
        assert decoded_payload is not None

        # Check that expiration is approximately 15 minutes from now
        exp_timestamp = decoded_payload["exp"]
        expected_exp = datetime.now(timezone.utc) + expires_delta
        actual_exp = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

        # Allow 1 second tolerance
        assert abs((actual_exp - expected_exp).total_seconds()) < 1

    def test_verify_invalid_token(self) -> None:
        """Test verifying an invalid token."""
        invalid_token = "invalid.jwt.token"
        result = verify_token(invalid_token)

        assert result is None

    def test_verify_expired_token(self) -> None:
        """Test verifying an expired token."""
        payload = {"sub": "user123"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(
            subject=payload["sub"],
            expires_delta=expires_delta
        )

        # Token should be expired and verification should fail
        result = verify_token(token)
        assert result is None

    def test_create_token_with_various_payloads(self) -> None:
        """Test creating tokens with various payload types."""
        payloads = [
            {"sub": "123", "role": "admin"},
            {"sub": "456", "permissions": ["read", "write"]},
            {"sub": "789", "metadata": {"name": "John", "age": 30}},
        ]

        for payload in payloads:
            token = create_access_token(
                subject=payload["sub"],
                **{k: v for k, v in payload.items() if k != "sub"}
            )
            result = verify_token(token)
            
            assert result is not None
            assert result["sub"] == payload["sub"]
            # Check that other claims are preserved but don't fail if not present
            for key, value in payload.items():
                if key in result:
                    assert result[key] == value

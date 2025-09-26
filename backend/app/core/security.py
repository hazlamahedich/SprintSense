"""Security utilities for authentication and password handling."""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return str(encoded_jwt)


def verify_token(token: str) -> Optional[dict[str, Any]]:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return dict(payload) if payload else None
    except JWTError:
        return None


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    if not isinstance(password, str):
        password = str(password)
    hashed = pwd_context.hash(password)
    return str(hashed)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    result = pwd_context.verify(plain_password, hashed_password)
    return bool(result)


async def get_current_user() -> dict[str, Any]:
    """Get current authenticated user from Supabase auth context.

    Returns:
        dict: User info with id and email
    """
    # In production this would verify JWT and get user info
    # For now return mock user
    return {"id": "00000000-0000-0000-0000-000000000000", "email": "dev@example.com"}


def get_password_hash(password: str) -> str:
    """Get password hash (alias for hash_password for consistency)."""
    return hash_password(password)

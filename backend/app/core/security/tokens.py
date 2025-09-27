"""Token verification and validation."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from pydantic import ValidationError

from app.core.config import settings
from app.core.logging import logger

def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    scopes: Optional[list[str]] = None,
    **extra_claims: Any
) -> str:
    """Create a new JWT access token.

    Args:
        subject: Token subject (usually user ID)
        expires_delta: Optional token lifetime
        scopes: Optional list of permission scopes
        **extra_claims: Additional claims to include

    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access"
    }

    if scopes:
        to_encode["scopes"] = scopes

    to_encode.update(extra_claims)

    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    except JWTError as e:
        logger.error(f"Failed to encode JWT token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create access token"
        )

def verify_token(token: str, raise_errors: bool = False) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token.

    Args:
        token: JWT token to verify

    Returns:
        Decoded token claims

    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Verify required claims
        if not all(k in payload for k in ["sub", "exp", "type"]):
            raise JWTError("Missing required claims")

        # Verify token type
        if payload["type"] != "access":
            raise JWTError("Invalid token type")

        # Verify expiration
        if datetime.utcfromtimestamp(payload["exp"]) < datetime.utcnow():
            raise JWTError("Token has expired")

        return payload

    except (JWTError, ValidationError) as e:
        logger.warning(f"Token validation failed: {e}")
        if raise_errors:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return None

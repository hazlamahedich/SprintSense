"""Security utilities for password hashing and authentication."""

import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID

from jose import JWTError, jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with a secure number of rounds.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        The hashed password as a string
    """
    # Generate a salt and hash the password
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds provides good security vs performance
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: The plain text password to verify
        hashed_password: The stored hash to verify against
        
    Returns:
        True if the password matches the hash, False otherwise
    """
    try:
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        # Return False for any exception (invalid hash format, etc.)
        return False


def is_password_strong(password: str) -> tuple[bool, list[str]]:
    """
    Check if a password meets security requirements.
    
    Args:
        password: The password to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one number")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain at least one special character")
    
    return len(errors) == 0, errors


def create_access_token(user_id: UUID, email: str) -> str:
    """
    Create a JWT access token for the user.
    
    Args:
        user_id: User's unique identifier
        email: User's email address
        
    Returns:
        The JWT token as a string
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),  # Subject - user ID
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),  # Issued at
        "type": "access_token"
    }
    
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT access token.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        The decoded payload if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Check if token type is correct
        if payload.get("type") != "access_token":
            return None
            
        # Check if required fields are present
        if not payload.get("sub") or not payload.get("email"):
            return None
            
        return payload
        
    except JWTError:
        return None

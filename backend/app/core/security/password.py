"""Password hashing and verification."""

from typing import Optional

import bcrypt

def get_password_hash(password: str) -> str:
    """Hash a password for storing.

    Args:
        password: Plain-text password

    Returns:
        Hashed password
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

def verify_password(plain_password: str, hashed_password: Optional[str]) -> bool:
    """Verify a stored password against a given password.

    Args:
        plain_password: Password to check
        hashed_password: Hashed password to check against

    Returns:
        bool: True if passwords match
    """
    if not hashed_password:
        return False

    try:
        return bcrypt.checkpw(
            plain_password.encode(),
            hashed_password.encode()
        )
    except (ValueError, TypeError):
        return False
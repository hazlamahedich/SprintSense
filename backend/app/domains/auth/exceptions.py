"""Authentication domain exceptions."""


class AuthenticationError(Exception):
    """Base exception for authentication errors."""
    pass


class UserAlreadyExistsError(AuthenticationError):
    """Exception raised when trying to register a user that already exists."""
    
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email '{email}' already exists")


class InvalidCredentialsError(AuthenticationError):
    """Exception raised when login credentials are invalid."""
    
    def __init__(self):
        super().__init__("Invalid email or password")


class WeakPasswordError(AuthenticationError):
    """Exception raised when password doesn't meet security requirements."""
    
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(f"Password validation failed: {', '.join(errors)}")


class InvalidEmailError(AuthenticationError):
    """Exception raised when email format is invalid."""
    
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Invalid email format: '{email}'")
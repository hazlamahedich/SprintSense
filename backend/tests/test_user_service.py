"""Tests for user service."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.models.user import User
from app.domains.schemas.user import UserCreateRequest, UserRead
from app.domains.services.user_service import UserService


@pytest.fixture
def mock_db_session() -> AsyncSession:
    """Create a mock database session."""
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def user_service(mock_db_session: AsyncSession) -> UserService:
    """Create a user service with mocked database session."""
    return UserService(mock_db_session)


@pytest.fixture
def sample_user_data() -> UserCreateRequest:
    """Sample user registration data."""
    return UserCreateRequest(
        email="test@example.com", full_name="Test User", password="TestPassword123"
    )


@pytest.fixture
def sample_user_model() -> User:
    """Sample user model instance."""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password_here",
        is_active=True,
    )
    # Mock the database fields that would be set automatically
    user.created_at = "2023-01-01T00:00:00Z"
    user.updated_at = None
    return user


class TestUserService:
    """Test user service functionality."""

    @pytest.mark.asyncio
    async def test_get_user_by_email_found(
        self,
        user_service: UserService,
        mock_db_session: AsyncSession,
        sample_user_model: User,
    ) -> None:
        """Test getting user by email when user exists."""
        # Mock the database query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_user_model
        mock_db_session.execute.return_value = mock_result

        user = await user_service.get_user_by_email("test@example.com")

        assert user is not None
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(
        self, user_service: UserService, mock_db_session: AsyncSession
    ) -> None:
        """Test getting user by email when user doesn't exist."""
        # Mock the database query result (no user found)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result

        user = await user_service.get_user_by_email("nonexistent@example.com")

        assert user is None
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_id_found(
        self,
        user_service: UserService,
        mock_db_session: AsyncSession,
        sample_user_model: User,
    ) -> None:
        """Test getting user by ID when user exists."""
        user_id = str(sample_user_model.id)

        # Mock the database query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_user_model
        mock_db_session.execute.return_value = mock_result

        user = await user_service.get_user_by_id(user_id)

        assert user is not None
        assert str(user.id) == user_id
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_success(
        self,
        user_service: UserService,
        mock_db_session: AsyncSession,
        sample_user_data: UserCreateRequest,
    ) -> None:
        """Test successful user creation."""
        # Mock that email doesn't exist
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result

        # Mock the created user after database operations
        created_user = User(
            id=uuid.uuid4(),
            email=sample_user_data.email,
            full_name=sample_user_data.full_name,
            hashed_password="hashed_password",
            is_active=True,
        )
        created_user.created_at = "2023-01-01T00:00:00Z"
        created_user.updated_at = None

        # Mock database operations
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        # Mock refresh to update the user object
        async def mock_refresh(user):
            # Simulate database setting the ID and timestamps
            user.id = created_user.id
            user.created_at = created_user.created_at
            user.updated_at = created_user.updated_at

        mock_db_session.refresh.side_effect = mock_refresh

        # Call the service method
        result = await user_service.create_user(sample_user_data)

        # Verify the result
        assert isinstance(result, UserRead)
        assert result.email == sample_user_data.email
        assert result.full_name == sample_user_data.full_name
        assert result.is_active is True

        # Verify database operations were called
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_email_already_exists(
        self,
        user_service: UserService,
        mock_db_session: AsyncSession,
        sample_user_data: UserCreateRequest,
        sample_user_model: User,
    ) -> None:
        """Test user creation when email already exists."""
        # Mock that email already exists
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_user_model
        mock_db_session.execute.return_value = mock_result

        # Should raise ValueError
        with pytest.raises(ValueError, match="Email already registered"):
            await user_service.create_user(sample_user_data)

        # Verify database operations were not called
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_is_email_taken_true(
        self,
        user_service: UserService,
        mock_db_session: AsyncSession,
        sample_user_model: User,
    ) -> None:
        """Test checking if email is taken when it exists."""
        # Mock that email exists
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_user_model
        mock_db_session.execute.return_value = mock_result

        result = await user_service.is_email_taken("test@example.com")

        assert result is True
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_email_taken_false(
        self, user_service: UserService, mock_db_session: AsyncSession
    ) -> None:
        """Test checking if email is taken when it doesn't exist."""
        # Mock that email doesn't exist
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await user_service.is_email_taken("nonexistent@example.com")

        assert result is False
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_user_success(
        self, user_service: UserService, mock_db_session: AsyncSession
    ) -> None:
        """Test successful user authentication."""
        # Create a user with a known password hash
        from app.core.security import hash_password

        password = "TestPassword123"
        hashed_password = hash_password(password)

        user_model = User(
            id=uuid.uuid4(),
            email="test@example.com",
            full_name="Test User",
            hashed_password=hashed_password,
            is_active=True,
        )

        # Mock database query to return the user
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = user_model
        mock_db_session.execute.return_value = mock_result

        # Authenticate with correct credentials
        result = await user_service.authenticate_user("test@example.com", password)

        assert result is not None
        assert result.email == "test@example.com"
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(
        self, user_service: UserService, mock_db_session: AsyncSession
    ) -> None:
        """Test user authentication with wrong password."""
        # Create a user with a known password hash
        from app.core.security import hash_password

        correct_password = "TestPassword123"
        wrong_password = "WrongPassword456"
        hashed_password = hash_password(correct_password)

        user_model = User(
            id=uuid.uuid4(),
            email="test@example.com",
            full_name="Test User",
            hashed_password=hashed_password,
            is_active=True,
        )

        # Mock database query to return the user
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = user_model
        mock_db_session.execute.return_value = mock_result

        # Authenticate with wrong password
        result = await user_service.authenticate_user(
            "test@example.com", wrong_password
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(
        self, user_service: UserService, mock_db_session: AsyncSession
    ) -> None:
        """Test user authentication when user doesn't exist."""
        # Mock database query to return None
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result

        # Try to authenticate non-existent user
        result = await user_service.authenticate_user(
            "nonexistent@example.com", "password"
        )

        assert result is None
        mock_db_session.execute.assert_called_once()


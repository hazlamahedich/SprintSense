"""Tests for LLM API key rotation functionality."""

import json
import asyncio
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError
from fastapi import HTTPException
from redis import Redis

from app.core.security.llm.key_rotation import LLMKeyRotationManager
from app.core.security.llm.key_scheduler import LLMKeyRotationScheduler

@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    redis = MagicMock(spec=Redis)
    redis.get.return_value = None
    redis.setex.return_value = True
    return redis

@pytest.fixture
def mock_boto3():
    """Create a mock boto3 client."""
    with patch('boto3.client') as mock:
        with patch.dict('os.environ', {
            'AWS_ACCESS_KEY_ID': 'test',
            'AWS_SECRET_ACCESS_KEY': 'test',
            'AWS_DEFAULT_REGION': 'us-east-1'
        }):
            secrets_manager = MagicMock()
            mock.return_value = secrets_manager
            yield secrets_manager

@pytest.fixture
def key_manager(mock_redis, mock_boto3):
    """Create a LLMKeyRotationManager instance with mocked dependencies."""
    return LLMKeyRotationManager(mock_redis)

class TestKeyRotationManager:
    """Test the LLMKeyRotationManager class."""

    def test_get_current_key_from_cache(self, key_manager, mock_redis):
        """Test retrieving a key that exists in cache."""
        mock_redis.get.return_value = b"cached-api-key"
        key = key_manager.get_current_key("openai")
        assert key == "cached-api-key"
        mock_redis.get.assert_called_once_with("llm_api_key:openai")

    def test_get_current_key_from_aws(self, key_manager, mock_boto3):
        """Test retrieving a key from AWS when not in cache."""
        mock_boto3.get_secret_value.return_value = {
            'SecretString': '{"openai": "aws-api-key"}'
        }
        key = key_manager.get_current_key("openai")
        assert key == "aws-api-key"
        mock_boto3.get_secret_value.assert_called_once()

    def test_get_current_key_not_found(self, key_manager, mock_boto3):
        """Test error when key doesn't exist."""
        mock_boto3.get_secret_value.return_value = {
            'SecretString': '{}'
        }
        with pytest.raises(HTTPException) as exc:
            key_manager.get_current_key("unknown-provider")
        assert exc.value.status_code == 500
        assert "No API key found" in exc.value.detail

    def test_get_current_key_aws_error(self, key_manager, mock_boto3):
        """Test handling AWS errors."""
        mock_boto3.get_secret_value.side_effect = ClientError(
            {"Error": {"Code": "InternalServiceError"}},
            "GetSecretValue"
        )
        with pytest.raises(HTTPException) as exc:
            key_manager.get_current_key("openai")
        assert exc.value.status_code == 500
        assert "Failed to retrieve API key" in exc.value.detail

    def test_rotate_key_success(self, key_manager, mock_boto3, mock_redis):
        """Test successful key rotation."""
        mock_boto3.get_secret_value.return_value = {
            'SecretString': '{"openai": "old-key"}'
        }
        key_manager.rotate_key("openai", "new-key")

        # Verify AWS update
        mock_boto3.put_secret_value.assert_called_once()
        assert "new-key" in mock_boto3.put_secret_value.call_args[1]['SecretString']

        # Verify cache update
        mock_redis.setex.assert_called_once()
        assert mock_redis.setex.call_args[0][0] == "llm_api_key:openai"
        assert mock_redis.setex.call_args[0][2] == "new-key"

    def test_rotate_key_aws_error(self, key_manager, mock_boto3):
        """Test handling AWS errors during rotation."""
        # Set up mock get_secret_value response first
        mock_boto3.get_secret_value.return_value = {
            'SecretString': json.dumps({"openai": "old-key"})
        }

        # Then set up put_secret_value error
        mock_boto3.put_secret_value.side_effect = ClientError(
            {"Error": {"Code": "InternalServiceError"}},
            "PutSecretValue"
        )

        with pytest.raises(HTTPException) as exc:
            key_manager.rotate_key("openai", "new-key")
        assert exc.value.status_code == 500
        assert "Failed to rotate API key" in exc.value.detail

    def test_check_rotation_needed_no_previous_rotation(self, key_manager, mock_boto3):
        """Test rotation check when no previous rotation exists."""
        mock_boto3.describe_secret.return_value = {}
        assert key_manager.check_rotation_needed("openai") is True

    def test_check_rotation_needed_recent_rotation(self, key_manager, mock_boto3):
        """Test rotation check with recent rotation."""
        mock_boto3.describe_secret.return_value = {
            'LastRotated': datetime.now().isoformat()
        }
        assert key_manager.check_rotation_needed("openai") is False

    def test_check_rotation_needed_old_rotation(self, key_manager, mock_boto3):
        """Test rotation check with old rotation."""
        old_date = (datetime.now() - timedelta(days=91)).isoformat()
        mock_boto3.describe_secret.return_value = {
            'LastRotated': old_date
        }
        assert key_manager.check_rotation_needed("openai") is True

@pytest.mark.asyncio
class TestKeyRotationScheduler:
    """Test the LLMKeyRotationScheduler class."""

    @pytest.fixture
    def scheduler(self, mock_redis):
        """Create a LLMKeyRotationScheduler instance."""
        return LLMKeyRotationScheduler(mock_redis)

    async def test_scheduler_start_stop(self, scheduler):
        """Test starting and stopping the scheduler."""
        # First, ensure the scheduler is not running
        if scheduler.scheduler.running:
            await scheduler.stop()
            await asyncio.sleep(0.1)  # Give it time to fully stop

        assert scheduler.scheduler.running is False

        # Now test the start
        await scheduler.start()
        assert scheduler.scheduler.running is True

        # Test the stop
        await scheduler.stop()
        await asyncio.sleep(0.1)  # Give it time to fully stop
        assert scheduler.scheduler.running is False

    async def test_check_and_rotate_keys(self, scheduler, mock_boto3):
        """Test the key rotation check job."""
        # Mock key_manager to simulate rotation needed
        scheduler.key_manager.check_rotation_needed = MagicMock(return_value=True)

        # Run the check
        await scheduler._check_and_rotate_keys()

        # Verify checks were performed
        assert scheduler.key_manager.check_rotation_needed.called

    async def test_monitor_key_status(self, scheduler, mock_boto3):
        """Test the key status monitoring job."""
        # Mock key_manager responses
        scheduler.key_manager.check_rotation_needed = MagicMock()
        scheduler.key_manager.check_rotation_needed.side_effect = [True, False]

        # Run monitoring
        await scheduler._monitor_key_status()

        # Verify monitoring was performed
        assert scheduler.key_manager.check_rotation_needed.call_count >= 1
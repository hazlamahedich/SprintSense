"""AWS Secrets Manager key rotation implementation for LLM API keys."""

import json
from datetime import datetime, timedelta
from typing import Dict, Optional

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException
from redis import Redis

from app.core.config import settings
from app.core.logging import logger

class LLMKeyRotationManager:
    """Manages automatic rotation of LLM API keys using AWS Secrets Manager."""

    def __init__(self, redis_client: Redis):
        """Initialize the key rotation manager.

        Args:
            redis_client: Redis client for caching current keys
        """
        self.secrets_manager = boto3.client('secretsmanager')
        self.redis_client = redis_client
        self.secret_id = settings.LLM_API_KEY_SECRET_ID
        self.rotation_period = timedelta(days=90)

    def get_current_key(self, provider: str) -> str:
        """Get the current API key for the specified LLM provider.

        Args:
            provider: The LLM provider name (e.g., 'openai', 'anthropic')

        Returns:
            str: The current API key

        Raises:
            HTTPException: If key cannot be retrieved
        """
        # Try cache first
        cache_key = f"llm_api_key:{provider}"
        cached_key = self.redis_client.get(cache_key)
        if cached_key:
            return cached_key.decode()

        try:
            # Get from AWS if not in cache
            secret = self._get_secret()
            if not secret or provider not in secret:
                raise HTTPException(
                    status_code=500,
                    detail=f"No API key found for provider {provider}"
                )

            # Cache the key
            key = secret[provider]
            self.redis_client.setex(
                cache_key,
                self.rotation_period.total_seconds(),
                key
            )
            return key

        except ClientError as e:
            logger.error(f"Failed to get API key: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve API key"
            )

    def rotate_key(self, provider: str, new_key: str) -> None:
        """Rotate the API key for the specified provider.

        Args:
            provider: The LLM provider name
            new_key: The new API key to use

        Raises:
            HTTPException: If rotation fails
        """
        try:
            # Get current secret
            secret = self._get_secret()
            if not secret:
                secret = {}

            # Update with new key
            secret[provider] = new_key
            self.secrets_manager.put_secret_value(
                SecretId=self.secret_id,
                SecretString=json.dumps(secret)
            )

            # Update cache
            cache_key = f"llm_api_key:{provider}"
            self.redis_client.setex(
                cache_key,
                self.rotation_period.total_seconds(),
                new_key
            )

            # Log rotation
            logger.info(f"Rotated API key for {provider}")

        except ClientError as e:
            logger.error(f"Failed to rotate API key: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to rotate API key"
            )

    def check_rotation_needed(self, provider: str) -> bool:
        """Check if key rotation is needed for the provider.

        Args:
            provider: The LLM provider name

        Returns:
            bool: True if rotation is needed
        """
        try:
            # Get last rotation time from metadata
            secret = self._get_secret_metadata()
            if not secret or 'LastRotated' not in secret:
                return True

            last_rotated = datetime.fromisoformat(secret['LastRotated'])
            return datetime.now() - last_rotated >= self.rotation_period

        except ClientError as e:
            logger.error(f"Failed to check rotation status: {str(e)}")
            return True

    def _get_secret(self) -> Optional[Dict[str, str]]:
        """Get the current secret from AWS Secrets Manager."""
        try:
            response = self.secrets_manager.get_secret_value(
                SecretId=self.secret_id
            )
            return json.loads(response['SecretString'])
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return None
            raise

    def _get_secret_metadata(self) -> Optional[Dict]:
        """Get secret metadata including last rotation time."""
        try:
            response = self.secrets_manager.describe_secret(
                SecretId=self.secret_id
            )
            return response
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return None
            raise
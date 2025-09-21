"""Redis-based caching service for quality metrics."""

import json
from typing import Any, Optional

import structlog
from redis.asyncio import Redis

logger = structlog.get_logger(__name__)


class CacheService:
    """Redis-based caching service with resilient operations."""

    def __init__(self, redis: Redis, prefix: str = "sprintsense"):
        """Initialize cache service.

        Args:
            redis: Redis connection
            prefix: Key prefix for namespacing (default: sprintsense)
        """
        self.redis = redis
        self.prefix = prefix

    def _key(self, key: str) -> str:
        """Get namespaced cache key.

        Args:
            key: Base key

        Returns:
            str: Namespaced key
        """
        return f"{self.prefix}:{key}"

    async def get(self, key: str, default: Any = None) -> Optional[Any]:
        """Get value from cache with error handling.

        Args:
            key: Cache key
            default: Default value if key missing or error occurs

        Returns:
            Optional[Any]: Cached value if available
        """
        try:
            value = await self.redis.get(self._key(key))
            if value is None:
                return default
            return json.loads(value)
        except Exception as e:
            logger.warning(
                "Cache get failed",
                key=key,
                error=str(e),
                error_type=type(e).__name__,
            )
            return default

    async def set(
        self,
        key: str,
        value: Any,
        expire_seconds: Optional[int] = None,
        nx: bool = False,
    ) -> bool:
        """Set value in cache with error handling.

        Args:
            key: Cache key
            value: Value to cache
            expire_seconds: Optional TTL in seconds
            nx: If True, only set if key doesn't exist

        Returns:
            bool: True if set successfully
        """
        try:
            return bool(
                await self.redis.set(
                    self._key(key),
                    json.dumps(value),
                    ex=expire_seconds,
                    nx=nx,
                )
            )
        except Exception as e:
            logger.warning(
                "Cache set failed",
                key=key,
                error=str(e),
                error_type=type(e).__name__,
            )
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache with error handling.

        Args:
            key: Cache key

        Returns:
            bool: True if deleted successfully
        """
        try:
            return bool(await self.redis.delete(self._key(key)))
        except Exception as e:
            logger.warning(
                "Cache delete failed",
                key=key,
                error=str(e),
                error_type=type(e).__name__,
            )
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            bool: True if key exists
        """
        try:
            return bool(await self.redis.exists(self._key(key)))
        except Exception as e:
            logger.warning(
                "Cache exists check failed",
                key=key,
                error=str(e),
                error_type=type(e).__name__,
            )
            return False

    async def expire(self, key: str, seconds: int) -> bool:
        """Set TTL on cache key.

        Args:
            key: Cache key
            seconds: TTL in seconds

        Returns:
            bool: True if TTL set successfully
        """
        try:
            return bool(await self.redis.expire(self._key(key), seconds))
        except Exception as e:
            logger.warning(
                "Cache expire failed",
                key=key,
                seconds=seconds,
                error=str(e),
                error_type=type(e).__name__,
            )
            return False

    async def pipeline(self) -> "RedisPipeline":
        """Get Redis pipeline for atomic operations.

        Returns:
            RedisPipeline: Pipeline wrapper
        """
        try:
            pipe = await self.redis.pipeline()
            return RedisPipeline(pipe, self.prefix)
        except Exception as e:
            logger.error(
                "Failed to create pipeline",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise


class RedisPipeline:
    """Wrapper for Redis pipeline with error handling."""

    def __init__(self, pipeline, prefix: str):
        """Initialize pipeline wrapper.

        Args:
            pipeline: Redis pipeline
            prefix: Key prefix for namespacing
        """
        self.pipeline = pipeline
        self.prefix = prefix

    def _key(self, key: str) -> str:
        """Get namespaced cache key.

        Args:
            key: Base key

        Returns:
            str: Namespaced key
        """
        return f"{self.prefix}:{key}"

    def set(
        self,
        key: str,
        value: Any,
        expire_seconds: Optional[int] = None,
        nx: bool = False,
    ) -> "RedisPipeline":
        """Add set operation to pipeline.

        Args:
            key: Cache key
            value: Value to cache
            expire_seconds: Optional TTL in seconds
            nx: If True, only set if key doesn't exist

        Returns:
            RedisPipeline: Self for chaining
        """
        self.pipeline.set(
            self._key(key),
            json.dumps(value),
            ex=expire_seconds,
            nx=nx,
        )
        return self

    def delete(self, key: str) -> "RedisPipeline":
        """Add delete operation to pipeline.

        Args:
            key: Cache key

        Returns:
            RedisPipeline: Self for chaining
        """
        self.pipeline.delete(self._key(key))
        return self

    def expire(self, key: str, seconds: int) -> "RedisPipeline":
        """Add expire operation to pipeline.

        Args:
            key: Cache key
            seconds: TTL in seconds

        Returns:
            RedisPipeline: Self for chaining
        """
        self.pipeline.expire(self._key(key), seconds)
        return self

    async def execute(self) -> list:
        """Execute pipeline with error handling.

        Returns:
            list: Pipeline results
        """
        try:
            return await self.pipeline.execute()
        except Exception as e:
            logger.error(
                "Pipeline execution failed",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

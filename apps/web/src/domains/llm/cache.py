from typing import Optional, Dict, Any
import json
import hashlib
from redis import Redis
from prometheus_client import Counter, Histogram
from pydantic import BaseSettings, Field

from .providers.base import LLMResponse

class LLMCacheSettings(BaseSettings):
    """Cache configuration settings."""
    ttl: int = Field(3600, env='LLM_CACHE_TTL')
    prefix: str = Field("llm:cache:", env='LLM_CACHE_PREFIX')
    max_items: int = Field(10000, env='LLM_CACHE_MAX_ITEMS')

    class Config:
        env_file = '.env'

class LLMCache:
    """Caching service for LLM responses."""

    def __init__(
        self,
        redis: Redis,
        settings: LLMCacheSettings = LLMCacheSettings()
    ):
        self.redis = redis
        self.settings = settings
        self.hits = Counter(
            'llm_cache_hits_total',
            'Total cache hits',
            ['provider']
        )
        self.misses = Counter(
            'llm_cache_misses_total',
            'Total cache misses',
            ['provider']
        )
        self.latency = Histogram(
            'llm_cache_operation_duration_seconds',
            'Cache operation duration'
        )

    def generate_cache_key(self, prompt: str, params: Dict[str, Any]) -> str:
        """Generate cache key from prompt and parameters."""
        # Sort params for consistent keys
        normalized_params = {
            k: v for k, v in sorted(params.items())
            if k not in {'temperature', 'top_p'}  # Exclude non-deterministic params
        }
        content = f"{prompt}:{json.dumps(normalized_params)}"
        key_hash = hashlib.sha256(content.encode()).hexdigest()
        return f"{self.settings.prefix}{key_hash}"

    async def get_cached_response(
        self,
        key: str,
        provider: str
    ) -> Optional[LLMResponse]:
        """Get cached response if available."""
        with self.latency.time():
            cached = await self.redis.get(key)
            if cached:
                self.hits.labels(provider=provider).inc()
                return LLMResponse.parse_raw(cached)
            self.misses.labels(provider=provider).inc()
            return None

    async def cache_response(
        self,
        key: str,
        response: LLMResponse,
        ttl: Optional[int] = None
    ) -> None:
        """Cache LLM response."""
        with self.latency.time():
            await self.redis.setex(
                key,
                ttl or self.settings.ttl,
                response.json()
            )

    async def invalidate(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern."""
        with self.latency.time():
            keys = await self.redis.keys(f"{self.settings.prefix}{pattern}")
            if keys:
                return await self.redis.delete(*keys)
            return 0

    async def cleanup_expired(self) -> None:
        """Clean up expired cache entries."""
        pattern = f"{self.settings.prefix}*"
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(
                cursor,
                match=pattern,
                count=100
            )
            for key in keys:
                if not await self.redis.ttl(key):
                    await self.redis.delete(key)
            if cursor == 0:
                break

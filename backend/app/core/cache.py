"""AsyncCache for caching data with async support."""

import time
from typing import Any, Dict, Optional


class AsyncCache:
    """Simple async-compatible cache with TTL support."""

    def __init__(self, ttl_seconds: int = 300):
        """Initialize cache with TTL in seconds."""
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl_seconds = ttl_seconds

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key not in self._cache:
            return None

        entry = self._cache[key]
        if time.time() > entry["expires_at"]:
            del self._cache[key]
            return None

        return entry["value"]

    async def set(self, key: str, value: Any) -> None:
        """Set value in cache with TTL."""
        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + self._ttl_seconds,
        }

    async def delete(self, key: str) -> None:
        """Delete a key from cache."""
        if key in self._cache:
            del self._cache[key]

    async def clear_pattern(self, pattern: str) -> None:
        """Delete all keys matching pattern.

        Example:
            await cache.clear_pattern("user:*:preferences")
        """
        # Simple wildcard matching for now - can be enhanced with regex later
        keys_to_delete = [
            key for key in self._cache.keys() if self._match_pattern(key, pattern)
        ]
        for key in keys_to_delete:
            await self.delete(key)

    async def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()

    def _match_pattern(self, key: str, pattern: str) -> bool:
        """Basic pattern matching with * wildcards."""
        if pattern == "*":
            return True

        if "*" not in pattern:
            return key == pattern

        parts = pattern.split("*")
        if not parts[0]:  # Pattern starts with *
            parts = parts[1:]

        start = 0
        for part in parts:
            if not part:  # Skip empty parts
                continue
            pos = key.find(part, start)
            if pos == -1:
                return False
            start = pos + len(part)

        # Check if pattern ends with * or if last part matches end of key
        return pattern.endswith("*") or key.endswith(parts[-1])

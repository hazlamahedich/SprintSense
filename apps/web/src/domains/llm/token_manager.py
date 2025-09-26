from typing import Dict, Any, Optional
from datetime import datetime
from redis import Redis
from prometheus_client import Counter, Gauge
from pydantic import BaseSettings, Field

class TokenQuotaSettings(BaseSettings):
    """Token quota configuration settings."""
    default_quota: int = Field(100000, env='LLM_DEFAULT_QUOTA')
    alert_threshold: float = Field(0.8, env='LLM_QUOTA_ALERT_THRESHOLD')
    quota_window: int = Field(2592000, env='LLM_QUOTA_WINDOW')  # 30 days in seconds
    prefix: str = Field("llm:quota:", env='LLM_QUOTA_PREFIX')

    class Config:
        env_file = '.env'

class TokenQuotaManager:
    """Manages token usage quotas for teams."""

    def __init__(
        self,
        redis: Redis,
        settings: TokenQuotaSettings = TokenQuotaSettings()
    ):
        self.redis = redis
        self.settings = settings
        self.tokens_used = Counter(
            'llm_tokens_total',
            'Total tokens used',
            ['team_id', 'provider']
        )
        self.quota_usage = Gauge(
            'llm_quota_usage_ratio',
            'Token quota usage ratio',
            ['team_id']
        )

    def _get_quota_key(self, team_id: str) -> str:
        """Generate quota key for team."""
        current_month = datetime.now().strftime("%Y-%m")
        return f"{self.settings.prefix}{team_id}:{current_month}"

    async def get_team_quota(self, team_id: str) -> int:
        """Get token quota for team."""
        quota = await self.redis.get(f"{self.settings.prefix}{team_id}:quota")
        return int(quota) if quota else self.settings.default_quota

    async def set_team_quota(self, team_id: str, quota: int) -> None:
        """Set token quota for team."""
        await self.redis.set(f"{self.settings.prefix}{team_id}:quota", quota)
        await self.update_usage_metrics(team_id)

    async def get_current_usage(self, team_id: str) -> int:
        """Get current token usage for team."""
        usage = await self.redis.get(self._get_quota_key(team_id))
        return int(usage) if usage else 0

    async def check_quota(
        self,
        team_id: str,
        tokens: int,
        provider: str
    ) -> bool:
        """Check if operation would exceed quota."""
        quota = await self.get_team_quota(team_id)
        usage = await self.get_current_usage(team_id)

        if usage + tokens > quota:
            return False

        # Track usage
        await self.redis.incrby(self._get_quota_key(team_id), tokens)
        await self.redis.expire(self._get_quota_key(team_id), self.settings.quota_window)

        # Update metrics
        self.tokens_used.labels(
            team_id=team_id,
            provider=provider
        ).inc(tokens)
        await self.update_usage_metrics(team_id)

        return True

    async def update_usage_metrics(self, team_id: str) -> None:
        """Update usage metrics for team."""
        usage = await self.get_current_usage(team_id)
        quota = await self.get_team_quota(team_id)
        ratio = usage / quota

        self.quota_usage.labels(team_id=team_id).set(ratio)

        # Check alert threshold
        if ratio >= self.settings.alert_threshold:
            # TODO: Trigger alert through alert manager
            pass

    async def reset_usage(self, team_id: str) -> None:
        """Reset usage counter for team."""
        await self.redis.delete(self._get_quota_key(team_id))
        await self.update_usage_metrics(team_id)

    async def get_usage_stats(self, team_id: str) -> Dict[str, Any]:
        """Get usage statistics for team."""
        usage = await self.get_current_usage(team_id)
        quota = await self.get_team_quota(team_id)
        return {
            'usage': usage,
            'quota': quota,
            'remaining': quota - usage,
            'usage_ratio': usage / quota if quota > 0 else 0,
            'reset_date': (
                datetime.now()
                .replace(day=1)
                .replace(month=datetime.now().month + 1)
                .strftime("%Y-%m-%d")
            )
        }

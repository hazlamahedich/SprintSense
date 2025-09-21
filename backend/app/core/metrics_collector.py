"""Background task for collecting quality metrics."""

import asyncio
import datetime
from typing import Optional

import structlog
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.metrics_logger import metrics_logger
from app.domains.schemas.quality_metrics import QualityMetricsResponse

logger = structlog.get_logger(__name__)

METRICS_CACHE_KEY = "quality_metrics:{team_id}"
METRICS_CACHE_TTL = 300  # 5 minutes
METRICS_UPDATE_INTERVAL = 60  # 1 minute
METRICS_LOCK_KEY = "quality_metrics_lock:{team_id}"
METRICS_LOCK_TTL = 30  # 30 seconds


class MetricsCollector:
    """Background task for collecting and caching quality metrics."""

    def __init__(self, redis: Redis, session_factory):
        """Initialize metrics collector.

        Args:
            redis: Redis connection
            session_factory: Factory function to create new database sessions
        """
        self.redis = redis
        self.session_factory = session_factory
        self.is_running = False

    async def start(self):
        """Start the metrics collector background task."""
        if self.is_running:
            return

        self.is_running = True
        while self.is_running:
            try:
                async with self.session_factory() as session:
                    await self._collect_metrics(session)
                await asyncio.sleep(METRICS_UPDATE_INTERVAL)
            except Exception as e:
                logger.exception(
                    "Error in metrics collector",
                    error=str(e),
                    error_type=type(e).__name__,
                )
                await asyncio.sleep(5)  # Short sleep on error

    async def stop(self):
        """Stop the metrics collector background task."""
        self.is_running = False

    async def _collect_metrics(self, session: AsyncSession):
        """Collect metrics for all active teams.

        Args:
            session: Database session
        """
        # Get all active teams
        result = await session.execute(
            text("SELECT id FROM teams WHERE is_active = true")
        )
        team_ids = [row[0] for row in result.fetchall()]

        # Collect metrics for each team
        for team_id in team_ids:
            try:
                await self._collect_team_metrics(session, str(team_id))
            except Exception as e:
                logger.error(
                    "Error collecting team metrics",
                    team_id=str(team_id),
                    error=str(e),
                )

    async def _collect_team_metrics(self, session: AsyncSession, team_id: str):
        """Collect metrics for a specific team.

        Args:
            session: Database session
            team_id: Team ID to collect metrics for
        """
        # Try to acquire lock
        lock_key = METRICS_LOCK_KEY.format(team_id=team_id)
        if not await self.redis.set(lock_key, "1", ex=METRICS_LOCK_TTL, nx=True):
            return  # Another process is collecting metrics

        try:
            # Get recommendation stats
            stats_result = await session.execute(
                text(
                    """
                    SELECT
                        COUNT(*) as total_count,
                        SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) as accepted_count,
                        AVG(confidence_score) as avg_confidence,
                        COUNT(CASE WHEN status = 'error' THEN 1 END) as error_count
                    FROM recommendations
                    WHERE team_id = :team_id
                    AND created_at >= NOW() - INTERVAL '1 hour'
                """
                ),
                {"team_id": team_id},
            )
            stats = stats_result.fetchone()

            # Get feedback distribution
            feedback_result = await session.execute(
                text(
                    """
                    SELECT feedback_type, COUNT(*)
                    FROM recommendation_feedback
                    WHERE team_id = :team_id
                    AND created_at >= NOW() - INTERVAL '1 hour'
                    GROUP BY feedback_type
                """
                ),
                {"team_id": team_id},
            )
            feedback_dist = {r[0]: r[1] for r in feedback_result}

            # Get feedback reasons
            reasons_result = await session.execute(
                text(
                    """
                    SELECT feedback_reason, COUNT(*)
                    FROM recommendation_feedback
                    WHERE team_id = :team_id
                    AND feedback_reason IS NOT NULL
                    AND created_at >= NOW() - INTERVAL '1 hour'
                    GROUP BY feedback_reason
                """
                ),
                {"team_id": team_id},
            )
            feedback_reasons = {r[0]: r[1] for r in reasons_result}

            # Calculate metrics
            total_count = stats[0] or 0
            error_rate = stats[3] / total_count if total_count > 0 else 0
            acceptance_rate = stats[1] / total_count if total_count > 0 else 0

            # Get performance metrics from Prometheus
            response_time = await metrics_logger.get_response_time_p95(team_id)
            request_rate = await metrics_logger.get_request_rate(team_id)
            cache_rate = await metrics_logger.get_cache_hit_rate(team_id)

            # Create metrics response
            metrics = QualityMetricsResponse(
                acceptance_rate=acceptance_rate,
                feedback_count=sum(feedback_dist.values()),
                feedback_distribution=feedback_dist,
                average_confidence=stats[2] or 0.0,
                feedback_reasons=feedback_reasons,
                error_rate=error_rate,
                response_time_p95=response_time,
                cache_hit_rate=cache_rate,
                request_rate=request_rate,
                created_at=datetime.datetime.utcnow().isoformat(),
                ttl=METRICS_CACHE_TTL,
            )

            # Cache the metrics
            cache_key = METRICS_CACHE_KEY.format(team_id=team_id)
            await self.redis.set(
                cache_key,
                metrics.model_dump_json(),
                ex=METRICS_CACHE_TTL,
            )

        finally:
            # Release lock
            await self.redis.delete(lock_key)

    async def get_cached_metrics(
        self, team_id: str
    ) -> Optional[QualityMetricsResponse]:
        """Get cached metrics for a team.

        Args:
            team_id: Team ID to get metrics for

        Returns:
            Optional[QualityMetricsResponse]: Cached metrics if available
        """
        cache_key = METRICS_CACHE_KEY.format(team_id=team_id)
        cached = await self.redis.get(cache_key)
        if cached:
            return QualityMetricsResponse.model_validate_json(cached)
        return None

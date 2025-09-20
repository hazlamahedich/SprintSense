"""
Business Metrics Service for AI Prioritization A/B Testing and Validation.

This service collects and analyzes business metrics to validate the effectiveness
of the AI prioritization algorithm and support A/B testing frameworks.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.domains.models.work_item import WorkItem, WorkItemStatus
from app.domains.schemas.ai_prioritization import BusinessMetrics, ScoredWorkItem


class BusinessMetricsService:
    """Service for collecting and analyzing business metrics for AI prioritization."""

    def __init__(self, db: AsyncSession, redis_client=None):
        self.db = db
        self.redis_client = redis_client

    async def track_scoring_event(
        self,
        team_id: uuid.UUID,
        user_id: uuid.UUID,
        request_data: Dict,
        response_data: Dict,
        generation_time_ms: float,
    ) -> None:
        """
        Track a scoring event for business metrics analysis.

        Args:
            team_id: Team identifier
            user_id: User who requested scoring
            request_data: Original request parameters
            response_data: Scoring response data
            generation_time_ms: Response generation time
        """
        try:
            # Create tracking event
            event_data = {
                "event_type": "ai_prioritization_scoring",
                "team_id": str(team_id),
                "user_id": str(user_id),
                "timestamp": datetime.utcnow().isoformat(),
                "request_metadata": {
                    "work_item_count": response_data.get("total_items", 0),
                    "include_metadata": request_data.get("include_metadata", False),
                    "mode": request_data.get("mode", "full"),
                    "specific_items": len(request_data.get("work_item_ids", [])) > 0,
                },
                "response_metadata": {
                    "generation_time_ms": generation_time_ms,
                    "algorithm_version": response_data.get("business_metrics", {}).get(
                        "algorithm_version", "1.0.0"
                    ),
                    "accuracy_score": response_data.get("business_metrics", {}).get(
                        "accuracy_score", 0.0
                    ),
                    "coverage_percentage": response_data.get(
                        "business_metrics", {}
                    ).get("coverage_percentage", 0.0),
                },
                "performance_metrics": {
                    "latency_requirement_met": generation_time_ms < 500,
                    "confidence_distribution": self._calculate_confidence_distribution(
                        response_data.get("scored_items", [])
                    ),
                },
            }

            # Store in Redis for real-time analytics (if available)
            if self.redis_client:
                try:
                    cache_key = f"business_metrics:scoring_events:{team_id}:{datetime.utcnow().date()}"
                    await self.redis_client.lpush(
                        cache_key, json.dumps(event_data, default=str)
                    )
                    await self.redis_client.expire(
                        cache_key, 86400 * 7
                    )  # 7 days retention
                except Exception as redis_error:
                    logger.warning(
                        f"Failed to cache business metrics event: {redis_error}"
                    )

            logger.info(
                f"Tracked AI prioritization scoring event for team {team_id}: "
                f"{response_data.get('total_items', 0)} items, {generation_time_ms:.2f}ms"
            )

        except Exception as e:
            logger.error(f"Failed to track scoring event: {e}")

    def _calculate_confidence_distribution(
        self, scored_items: List[Dict]
    ) -> Dict[str, int]:
        """Calculate distribution of confidence levels in scored items."""
        distribution = {"high": 0, "medium": 0, "low": 0}

        for item in scored_items:
            confidence = item.get("confidence_level", "low")
            if confidence in distribution:
                distribution[confidence] += 1

        return distribution

    async def calculate_algorithm_effectiveness(
        self,
        team_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, float]:
        """
        Calculate algorithm effectiveness metrics over a time period.

        Args:
            team_id: Team to analyze
            start_date: Start of analysis period
            end_date: End of analysis period

        Returns:
            Dictionary with effectiveness metrics
        """
        try:
            # Query work items completed in the period
            completed_items_query = select(WorkItem).where(
                and_(
                    WorkItem.team_id == team_id,
                    WorkItem.status == WorkItemStatus.DONE,
                    WorkItem.updated_at >= start_date,
                    WorkItem.updated_at <= end_date,
                )
            )

            result = await self.db.execute(completed_items_query)
            completed_items = result.scalars().all()

            if not completed_items:
                return {
                    "completion_rate": 0.0,
                    "average_completion_time": 0.0,
                    "high_priority_completion_rate": 0.0,
                    "algorithm_adoption_score": 0.0,
                }

            # Calculate metrics
            total_items = len(completed_items)
            high_priority_items = [
                item for item in completed_items if item.priority >= 7.0
            ]
            high_priority_completion_rate = (
                len(high_priority_items) / total_items if total_items > 0 else 0.0
            )

            # Calculate average completion time
            completion_times = []
            for item in completed_items:
                if item.created_at and item.updated_at:
                    completion_time = (
                        item.updated_at - item.created_at
                    ).total_seconds() / 3600  # hours
                    completion_times.append(completion_time)

            average_completion_time = (
                sum(completion_times) / len(completion_times)
                if completion_times
                else 0.0
            )

            # Algorithm adoption score based on priority correlation
            # Higher score if items with higher priorities are completed faster
            algorithm_adoption_score = self._calculate_adoption_score(completed_items)

            return {
                "completion_rate": total_items
                / max(1, await self._get_total_backlog_items(team_id)),
                "average_completion_time": average_completion_time,
                "high_priority_completion_rate": high_priority_completion_rate,
                "algorithm_adoption_score": algorithm_adoption_score,
            }

        except Exception as e:
            logger.error(f"Failed to calculate algorithm effectiveness: {e}")
            return {
                "completion_rate": 0.0,
                "average_completion_time": 0.0,
                "high_priority_completion_rate": 0.0,
                "algorithm_adoption_score": 0.0,
            }

    def _calculate_adoption_score(self, completed_items: List[WorkItem]) -> float:
        """
        Calculate how well the team is following AI priority suggestions.

        Returns a score between 0.0 and 1.0 where 1.0 indicates perfect adoption.
        """
        if len(completed_items) < 2:
            return 0.0

        # Sort by completion date
        items_by_completion = sorted(
            completed_items, key=lambda x: x.updated_at or datetime.min
        )

        # Calculate if higher priority items were completed first
        correct_order_count = 0
        total_comparisons = 0

        for i in range(len(items_by_completion)):
            for j in range(i + 1, len(items_by_completion)):
                item1 = items_by_completion[i]
                item2 = items_by_completion[j]

                # item1 was completed before item2
                if (item1.priority or 0.0) >= (item2.priority or 0.0):
                    correct_order_count += 1

                total_comparisons += 1

        return correct_order_count / total_comparisons if total_comparisons > 0 else 0.0

    async def _get_total_backlog_items(self, team_id: uuid.UUID) -> int:
        """Get total number of backlog items for completion rate calculation."""
        try:
            backlog_query = select(func.count(WorkItem.id)).where(
                and_(
                    WorkItem.team_id == team_id,
                    WorkItem.status.in_(
                        [
                            WorkItemStatus.BACKLOG,
                            WorkItemStatus.TODO,
                            WorkItemStatus.IN_PROGRESS,
                        ]
                    ),
                )
            )

            result = await self.db.execute(backlog_query)
            return result.scalar() or 0

        except Exception:
            return 1  # Avoid division by zero

    async def get_ab_test_metrics(
        self,
        team_id: uuid.UUID,
        variant_a: str = "algorithm_v1",
        variant_b: str = "algorithm_v2",
        days: int = 30,
    ) -> Dict[str, Dict[str, float]]:
        """
        Get A/B test metrics comparing two algorithm variants.

        Args:
            team_id: Team to analyze
            variant_a: First algorithm variant identifier
            variant_b: Second algorithm variant identifier
            days: Number of days to analyze

        Returns:
            Metrics for both variants for comparison
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        try:
            # Get cached metrics for both variants
            metrics_a = await self._get_variant_metrics(
                team_id, variant_a, start_date, end_date
            )
            metrics_b = await self._get_variant_metrics(
                team_id, variant_b, start_date, end_date
            )

            return {
                variant_a: metrics_a,
                variant_b: metrics_b,
                "comparison": self._compare_variants(metrics_a, metrics_b),
            }

        except Exception as e:
            logger.error(f"Failed to get A/B test metrics: {e}")
            return {variant_a: {}, variant_b: {}, "comparison": {}}

    async def _get_variant_metrics(
        self,
        team_id: uuid.UUID,
        variant: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, float]:
        """Get metrics for a specific algorithm variant."""
        # In a real implementation, this would query metrics stored with variant tags
        # For now, we'll return baseline metrics
        return await self.calculate_algorithm_effectiveness(
            team_id, start_date, end_date
        )

    def _compare_variants(
        self,
        metrics_a: Dict[str, float],
        metrics_b: Dict[str, float],
    ) -> Dict[str, float]:
        """Compare two variants and calculate improvement percentages."""
        comparison = {}

        for key in metrics_a.keys():
            if key in metrics_b:
                value_a = metrics_a[key]
                value_b = metrics_b[key]

                if value_a > 0:
                    improvement = ((value_b - value_a) / value_a) * 100
                    comparison[f"{key}_improvement_pct"] = improvement
                else:
                    comparison[f"{key}_improvement_pct"] = 0.0

        return comparison

    async def get_performance_dashboard_data(
        self,
        team_id: uuid.UUID,
        days: int = 7,
    ) -> Dict[str, any]:
        """
        Get dashboard data for performance monitoring.

        Args:
            team_id: Team identifier
            days: Number of days of data to include

        Returns:
            Dashboard data including usage stats, performance metrics, and trends
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        try:
            dashboard_data = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days,
                },
                "usage_stats": await self._get_usage_statistics(
                    team_id, start_date, end_date
                ),
                "performance_metrics": await self._get_performance_statistics(
                    team_id, start_date, end_date
                ),
                "algorithm_effectiveness": await self.calculate_algorithm_effectiveness(
                    team_id, start_date, end_date
                ),
                "trend_data": await self._get_trend_data(team_id, start_date, end_date),
            }

            return dashboard_data

        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {"error": "Failed to generate dashboard data"}

    async def _get_usage_statistics(
        self,
        team_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, int]:
        """Get usage statistics for the specified period."""
        # In a real implementation, this would query stored events
        # For now, return mock data structure
        return {
            "total_scoring_requests": 0,
            "unique_users": 0,
            "average_items_per_request": 0,
            "fast_mode_usage_pct": 0,
        }

    async def _get_performance_statistics(
        self,
        team_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, float]:
        """Get performance statistics for the specified period."""
        # In a real implementation, this would analyze stored performance metrics
        return {
            "average_response_time_ms": 0.0,
            "p95_response_time_ms": 0.0,
            "latency_sla_compliance_pct": 100.0,
            "error_rate_pct": 0.0,
            "cache_hit_rate_pct": 0.0,
        }

    async def _get_trend_data(
        self,
        team_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict[str, any]]:
        """Get daily trend data for charting."""
        trends = []
        current_date = start_date

        while current_date <= end_date:
            trends.append(
                {
                    "date": current_date.date().isoformat(),
                    "scoring_requests": 0,
                    "average_response_time": 0.0,
                    "completion_rate": 0.0,
                }
            )
            current_date += timedelta(days=1)

        return trends

    async def validate_business_impact(
        self,
        team_id: uuid.UUID,
        before_date: datetime,
        after_date: datetime,
    ) -> Dict[str, any]:
        """
        Validate business impact by comparing metrics before and after AI implementation.

        Args:
            team_id: Team to analyze
            before_date: Date when AI prioritization was implemented
            after_date: End date for after period

        Returns:
            Business impact validation results
        """
        try:
            # Calculate periods
            period_length = (before_date - (before_date - timedelta(days=30))).days
            before_start = before_date - timedelta(days=period_length)
            after_end = after_date

            # Get metrics for both periods
            before_metrics = await self.calculate_algorithm_effectiveness(
                team_id, before_start, before_date
            )
            after_metrics = await self.calculate_algorithm_effectiveness(
                team_id, before_date, after_end
            )

            # Calculate improvements
            improvements = {}
            for key in before_metrics.keys():
                if key in after_metrics:
                    before_val = before_metrics[key]
                    after_val = after_metrics[key]

                    if before_val > 0:
                        improvement_pct = ((after_val - before_val) / before_val) * 100
                        improvements[f"{key}_improvement"] = improvement_pct
                    else:
                        improvements[f"{key}_improvement"] = 0.0

            return {
                "validation_period": {
                    "before_period": f"{before_start.date()} to {before_date.date()}",
                    "after_period": f"{before_date.date()} to {after_end.date()}",
                },
                "before_metrics": before_metrics,
                "after_metrics": after_metrics,
                "improvements": improvements,
                "business_impact_score": self._calculate_business_impact_score(
                    improvements
                ),
                "recommendation": self._generate_recommendation(improvements),
            }

        except Exception as e:
            logger.error(f"Failed to validate business impact: {e}")
            return {"error": "Failed to validate business impact"}

    def _calculate_business_impact_score(self, improvements: Dict[str, float]) -> float:
        """Calculate overall business impact score from 0.0 to 1.0."""
        if not improvements:
            return 0.0

        # Weight different metrics by business importance
        weights = {
            "completion_rate_improvement": 0.3,
            "average_completion_time_improvement": 0.25,
            "high_priority_completion_rate_improvement": 0.3,
            "algorithm_adoption_score_improvement": 0.15,
        }

        weighted_score = 0.0
        total_weight = 0.0

        for metric, improvement in improvements.items():
            if metric in weights:
                # Normalize improvement to 0-1 scale (cap at 100% improvement)
                normalized_improvement = min(max(improvement / 100, -1), 1)
                weighted_score += weights[metric] * normalized_improvement
                total_weight += weights[metric]

        return max(0.0, weighted_score / total_weight) if total_weight > 0 else 0.0

    def _generate_recommendation(self, improvements: Dict[str, float]) -> str:
        """Generate business recommendation based on improvements."""
        avg_improvement = (
            sum(improvements.values()) / len(improvements) if improvements else 0.0
        )

        if avg_improvement > 20:
            return "Strong positive impact detected. Continue using AI prioritization and consider expanding to other teams."
        elif avg_improvement > 10:
            return "Positive impact observed. Monitor continued performance and gather more data."
        elif avg_improvement > 0:
            return "Slight positive impact. Consider algorithm tuning or additional training data."
        elif avg_improvement > -10:
            return "Minimal impact detected. Review algorithm parameters and team adoption."
        else:
            return "Negative impact detected. Investigate algorithm issues and consider reverting to manual prioritization."

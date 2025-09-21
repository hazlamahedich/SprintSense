from typing import Dict, List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.domains.models.work_item import WorkItem
from app.schemas.recommendation import WorkItemRecommendation
from app.schemas.quality_metrics import QualityMetrics
from app.core.cache import AsyncCache
from app.core.ai_service import AIService
from app.core.circuit_breaker import CircuitBreaker


class RecommendationsService:
    def __init__(self):
        self.cache = AsyncCache(ttl_seconds=300)  # 5 minutes TTL
        self.ai_service = AIService()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5, recovery_timeout=60, name="ai_recommendations"
        )

    async def get_recommendations(
        self,
        session: AsyncSession,
        team_id: str,
        min_confidence: float = 0.7,
        limit: int = 5,
    ) -> List[WorkItemRecommendation]:
        """
        Get AI-powered work item recommendations for a team.
        Includes caching and circuit breaker patterns.
        """
        cache_key = f"recommendations:{team_id}:{min_confidence}:{limit}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        try:
            # Get team's work items for pattern analysis
            work_items = await self._get_team_work_items(session, team_id)

            # Get team velocity metrics
            velocity_metrics = await self._calculate_team_velocity(session, team_id)

            # Generate recommendations using AI service with circuit breaker
            async with self.circuit_breaker:
                recommendations = await self.ai_service.generate_recommendations(
                    work_items=work_items,
                    velocity_metrics=velocity_metrics,
                    min_confidence=min_confidence,
                    limit=limit,
                )

            # Cache the results
            await self.cache.set(cache_key, recommendations)
            return recommendations

        except Exception as e:
            # Log error details
            print(f"Error generating recommendations: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to generate recommendations"
            )

    async def _get_team_work_items(
        self,
        session: AsyncSession,
        team_id: str,
        limit: int = 1000,  # Last 1000 items for pattern analysis
    ) -> List[Dict]:
        query = (
            select(WorkItem)
            .where(WorkItem.team_id == team_id)
            .order_by(WorkItem.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def _calculate_team_velocity(
        self, session: AsyncSession, team_id: str
    ) -> Dict:
        """Calculate team velocity metrics based on historical data."""
        # Get completed work items in the last 3 months
        three_months_ago = func.now() - func.interval("3 months")
        query = select(WorkItem).where(
            WorkItem.team_id == team_id, WorkItem.completed_at >= three_months_ago
        )
        result = await session.execute(query)
        completed_items = result.scalars().all()

        # Calculate velocity metrics
        total_story_points = sum(item.story_points or 0 for item in completed_items)
        avg_completion_time = self._calculate_avg_completion_time(completed_items)
        completion_rate = len(completed_items) / 90  # Items per day

        return {
            "story_points_velocity": total_story_points / 90,  # Points per day
            "avg_completion_time": avg_completion_time,
            "completion_rate": completion_rate,
        }

    def _calculate_avg_completion_time(self, items: List[WorkItem]) -> float:
        """Calculate average completion time in hours."""
        completion_times = []
        for item in items:
            if item.completed_at and item.created_at:
                delta = item.completed_at - item.created_at
                completion_times.append(
                    delta.total_seconds() / 3600
                )  # Convert to hours

        return sum(completion_times) / len(completion_times) if completion_times else 0

    async def accept_recommendation(
        self, session: AsyncSession, recommendation_id: str
    ) -> None:
        """Handle recommendation acceptance and feedback."""
        try:
            # Record acceptance feedback
            await self._record_feedback(
                session, recommendation_id, feedback_type="accepted"
            )

            # Invalidate cache for related recommendations
            await self._invalidate_related_cache(recommendation_id)

        except Exception as e:
            print(f"Error accepting recommendation: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to accept recommendation"
            )

    async def provide_feedback(
        self,
        session: AsyncSession,
        recommendation_id: str,
        feedback_type: str,
        reason: Optional[str] = None,
    ) -> None:
        """Record feedback for recommendation improvement."""
        try:
            await self._record_feedback(
                session, recommendation_id, feedback_type=feedback_type, reason=reason
            )

            # Invalidate cache if feedback affects recommendations
            if feedback_type in ["not_useful", "modified"]:
                await self._invalidate_related_cache(recommendation_id)

        except Exception as e:
            print(f"Error recording feedback: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to record feedback")

    async def _record_feedback(
        self,
        session: AsyncSession,
        recommendation_id: str,
        feedback_type: str,
        reason: Optional[str] = None,
    ) -> None:
        """Record recommendation feedback for model improvement."""
        feedback = {
            "recommendation_id": recommendation_id,
            "type": feedback_type,
            "reason": reason,
            "timestamp": func.now(),
        }

        # Send feedback to AI service for model improvement
        await self.ai_service.record_feedback(feedback)

    async def _invalidate_related_cache(self, recommendation_id: str) -> None:
        """Invalidate cached recommendations related to the given recommendation."""
        # For now, we'll just clear all recommendation caches
        # TODO: Implement more granular cache invalidation
        await self.cache.clear_pattern("recommendations:*")

    async def get_quality_metrics(self, session: AsyncSession, team_id: str) -> QualityMetrics:
        """Get quality metrics for recommendations."""
        cache_key = f"quality:{team_id}"
        try:
            # Return cached if available
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

            # Get the counts from last 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)

            # Get total recommendations and acceptance counts
            total_query = select(func.count('*')).select_from(WorkItem).\
                where(
                    WorkItem.team_id == team_id,
                    WorkItem.created_at >= thirty_days_ago
                )
            total_result = await session.execute(total_query)
            total_recommendations = total_result.scalar() or 0

            # Get accepted and archived counts
            status_query = (
                select(WorkItem.status, func.count('*').label('count'))
                .where(
                    WorkItem.team_id == team_id,
                    WorkItem.created_at >= thirty_days_ago
                )
                .group_by(WorkItem.status)
            )
            status_result = await session.execute(status_query)
            status_counts = {status: count for status, count in status_result.all()}

            accepted_count = sum(count for status, count in status_counts.items()
                               if status != 'archived')

            # Get recent acceptance count
            recent_query = select(func.count('*')).select_from(WorkItem).\
                where(
                    WorkItem.team_id == team_id,
                    WorkItem.created_at >= seven_days_ago,
                    WorkItem.status != 'archived'
                )
            recent_result = await session.execute(recent_query)
            recent_accepted = recent_result.scalar() or 0

            # Get average confidence scores (stored in priority field)
            confidence_query = select(func.avg(WorkItem.priority)).\
                where(
                    WorkItem.team_id == team_id,
                    WorkItem.created_at >= thirty_days_ago
                )
            confidence_result = await session.execute(confidence_query)
            avg_confidence = confidence_result.scalar() or 0.0

            # Get feedback reasons distribution
            feedback_query = select(
                WorkItem.feedback_reason,
                func.count('*').label('count')
            ).select_from(WorkItem).\
                where(
                    WorkItem.team_id == team_id,
                    WorkItem.created_at >= thirty_days_ago,
                    WorkItem.status == 'archived',
                    WorkItem.feedback_reason.isnot(None)
                ).group_by(WorkItem.feedback_reason)

            feedback_result = await session.execute(feedback_query)
            feedback_counts = feedback_result.all()
            feedback_reasons = {reason: count for reason, count in feedback_counts}
            total_feedback = sum(feedback_reasons.values())

            top_reason = max(feedback_counts, key=lambda x: x[1])[0] if feedback_counts else None

            # Get performance metrics from monitoring (synthetic data for now)
            # In production, these would come from actual monitoring metrics
            ui_resp_time = 250  # Example: 250ms average UI response time
            backend_resp_95th = 150  # Example: 150ms 95th percentile backend time

            result = QualityMetrics(
                acceptance_rate=accepted_count / total_recommendations if total_recommendations > 0 else 0,
                recent_acceptance_count=recent_accepted,
                avg_confidence=avg_confidence,
                total_recommendations=total_recommendations,
                top_feedback_reason=top_reason,
                feedback_count=total_feedback,
                feedback_reasons=feedback_reasons,
                ui_response_time=ui_resp_time,
                backend_response_time_95th=backend_resp_95th,
                updated_at=datetime.utcnow()
            )

            # Cache result
            await self.cache.set(cache_key, result)
            return result

        except Exception as e:
            # On error, try serve cached result
            cached = await self.cache.get(cache_key)
            if cached:
                return cached
            print(f"Error calculating quality metrics: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to calculate quality metrics"
            )

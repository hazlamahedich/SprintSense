"""Schemas for recommendation quality metrics."""

from datetime import datetime

from pydantic import BaseModel


class QualityMetrics(BaseModel):
    """Model for aggregated recommendation quality metrics."""

    acceptance_rate: float
    recent_acceptance_count: int
    avg_confidence: float
    total_recommendations: int
    top_feedback_reason: str | None
    feedback_count: int
    ui_response_time: float
    backend_response_time_95th: float
    feedback_reasons: dict[str, int]
    updated_at: datetime = None

"""Schemas for quality metrics endpoints."""

from typing import Dict

from pydantic import BaseModel, Field


class QualityMetricsResponse(BaseModel):
    """Response schema for quality metrics endpoint."""

    acceptance_rate: float = Field(
        ...,
        description="Percentage of recommendations accepted by users",
        ge=0.0,
        le=1.0,
    )
    feedback_count: int = Field(
        ...,
        description="Total number of feedback responses received",
        ge=0,
    )
    feedback_distribution: Dict[str, float] = Field(
        ...,
        description="Distribution of feedback types (useful, not_useful, etc.)",
    )
    average_confidence: float = Field(
        ...,
        description="Average confidence score of recommendations",
        ge=0.0,
        le=1.0,
    )
    feedback_reasons: Dict[str, int] = Field(
        ...,
        description="Count of feedback reasons (too_complex, not_relevant, etc.)",
    )
    error_rate: float = Field(
        ...,
        description="Rate of recommendation errors in the last hour",
        ge=0.0,
        le=1.0,
    )
    response_time_p95: float = Field(
        ...,
        description="95th percentile response time in seconds",
        ge=0.0,
    )
    cache_hit_rate: float = Field(
        ...,
        description="Cache hit rate for recommendations",
        ge=0.0,
        le=1.0,
    )
    request_rate: float = Field(
        ...,
        description="Average requests per second in the last minute",
        ge=0.0,
    )
    created_at: str = Field(
        ...,
        description="Timestamp when these metrics were collected",
    )
    ttl: int = Field(
        ...,
        description="Time in seconds until these metrics expire",
        ge=0,
    )

"""AI Prioritization Pydantic schemas for request/response validation."""

import uuid
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, field_validator


class AIPrioritizationRequest(BaseModel):
    """Schema for AI prioritization request."""

    work_item_ids: Optional[List[uuid.UUID]] = None  # Optional: specific items to score
    include_metadata: bool = False  # Optional: include scoring details
    mode: Literal["full", "suggestion", "clustering"] = (
        "full"  # Support different workflow modes
    )

    @field_validator("work_item_ids")
    @classmethod
    def validate_work_item_ids(
        cls, v: Optional[List[uuid.UUID]]
    ) -> Optional[List[uuid.UUID]]:
        """Validate work item IDs if provided."""
        if v is not None:
            if len(v) > 1000:
                raise ValueError("Cannot score more than 1000 work items at once")
            # Remove duplicates while preserving order
            seen = set()
            unique_ids = []
            for id in v:
                if id not in seen:
                    seen.add(id)
                    unique_ids.append(id)
            return unique_ids
        return v


class MatchedGoal(BaseModel):
    """Schema for matched goal metadata."""

    goal_id: uuid.UUID
    goal_title: str
    match_strength: float
    matched_keywords: List[str]

    @field_validator("match_strength")
    @classmethod
    def validate_match_strength(cls, v: float) -> float:
        """Validate match strength is within bounds."""
        if v < 0.0 or v > 10.0:
            raise ValueError("Match strength must be between 0.0 and 10.0")
        return v


class ScoringMetadata(BaseModel):
    """Schema for detailed scoring metadata."""

    matched_goals: List[MatchedGoal]
    base_score: float
    priority_adjustment: float
    clustering_similarity: float

    @field_validator("base_score", "priority_adjustment")
    @classmethod
    def validate_scores(cls, v: float) -> float:
        """Validate scores are within bounds."""
        if v < 0.0:
            raise ValueError("Scores cannot be negative")
        return v

    @field_validator("clustering_similarity")
    @classmethod
    def validate_clustering_similarity(cls, v: float) -> float:
        """Validate clustering similarity is within bounds."""
        if v < 0.0 or v > 1.0:
            raise ValueError("Clustering similarity must be between 0.0 and 1.0")
        return v


class ScoredWorkItem(BaseModel):
    """Schema for scored work item."""

    work_item_id: uuid.UUID
    title: str
    current_priority: float
    ai_score: float
    suggested_rank: int
    confidence_level: Literal["high", "medium", "low"]  # User confidence indicator
    explanation: str  # Human-readable reasoning
    scoring_metadata: Optional[ScoringMetadata] = None  # If include_metadata=true

    @field_validator("ai_score")
    @classmethod
    def validate_ai_score(cls, v: float) -> float:
        """Validate AI score is within bounds."""
        if v < 0.0 or v > 10.0:
            raise ValueError("AI score must be between 0.0 and 10.0")
        return v

    @field_validator("suggested_rank")
    @classmethod
    def validate_suggested_rank(cls, v: int) -> int:
        """Validate suggested rank is positive."""
        if v < 1:
            raise ValueError("Suggested rank must be positive (1-based)")
        return v

    @field_validator("current_priority")
    @classmethod
    def validate_current_priority(cls, v: float) -> float:
        """Validate current priority is non-negative."""
        if v < 0.0:
            raise ValueError("Current priority cannot be negative")
        return v


class BusinessMetrics(BaseModel):
    """Schema for business value validation metrics."""

    accuracy_score: float  # Average confidence as numeric value
    coverage_percentage: float  # Percentage of items with non-zero scores
    algorithm_version: str

    @field_validator("accuracy_score")
    @classmethod
    def validate_accuracy_score(cls, v: float) -> float:
        """Validate accuracy score is within bounds."""
        if v < 0.0 or v > 1.0:
            raise ValueError("Accuracy score must be between 0.0 and 1.0")
        return v

    @field_validator("coverage_percentage")
    @classmethod
    def validate_coverage_percentage(cls, v: float) -> float:
        """Validate coverage percentage is within bounds."""
        if v < 0.0 or v > 100.0:
            raise ValueError("Coverage percentage must be between 0.0 and 100.0")
        return v


class AIPrioritizationResponse(BaseModel):
    """Schema for AI prioritization response."""

    scored_items: List[ScoredWorkItem]
    total_items: int
    generation_time_ms: int
    business_metrics: BusinessMetrics  # For business value validation
    warning: Optional[str] = (
        None  # Optional warning message (e.g., "no_goals_configured")
    )

    @field_validator("total_items")
    @classmethod
    def validate_total_items(cls, v: int) -> int:
        """Validate total items count is non-negative."""
        if v < 0:
            raise ValueError("Total items count cannot be negative")
        return v

    @field_validator("generation_time_ms")
    @classmethod
    def validate_generation_time_ms(cls, v: int) -> int:
        """Validate generation time is non-negative."""
        if v < 0:
            raise ValueError("Generation time cannot be negative")
        return v

    model_config = ConfigDict(from_attributes=True)


class AIPrioritizationErrorResponse(BaseModel):
    """Schema for AI prioritization error responses."""

    error_code: str
    message: str
    details: Optional[dict] = None
    recovery_action: str
    retry_after: Optional[int] = None  # Seconds to wait before retry

    model_config = ConfigDict(from_attributes=True)

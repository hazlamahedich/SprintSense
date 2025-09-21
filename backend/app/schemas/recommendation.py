from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class WorkItemType(str, Enum):
    story = "story"
    bug = "bug"
    task = "task"


class FeedbackType(str, Enum):
    not_useful = "not_useful"
    accepted = "accepted"
    modified = "modified"


class WorkItemRecommendation(BaseModel):
    id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=2000)
    type: WorkItemType
    suggested_priority: float = Field(..., ge=0)
    confidence_scores: Dict[str, float] = Field(
        ..., description="Confidence scores for different aspects of the recommendation"
    )
    reasoning: str = Field(..., max_length=1000)
    patterns_identified: List[str]
    team_velocity_factor: float = Field(..., ge=0, le=1)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "rec_123",
                "title": "Implement user authentication caching",
                "description": "Add Redis caching layer for user authentication tokens to improve performance",
                "type": "story",
                "suggested_priority": 0.85,
                "confidence_scores": {
                    "title": 0.9,
                    "description": 0.85,
                    "type": 0.95,
                    "priority": 0.8,
                },
                "reasoning": "Pattern analysis shows multiple performance-related stories with high success rate",
                "patterns_identified": [
                    "performance_optimization",
                    "authentication_system",
                    "caching_implementation",
                ],
                "team_velocity_factor": 0.75,
            }
        }


class RecommendationFeedback(BaseModel):
    type: FeedbackType
    reason: Optional[str] = Field(None, max_length=500)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "type": "not_useful",
                "reason": "The suggested priority doesn't align with our current sprint goals",
                "timestamp": "2025-09-21T02:10:56Z",
            }
        }

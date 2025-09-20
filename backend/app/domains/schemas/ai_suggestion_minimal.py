"""Minimal Pydantic schemas for AI suggestions API testing."""

from typing import List, Literal, Optional

from pydantic import BaseModel


class BatchSuggestionRequest(BaseModel):
    """Request model for batch suggestion generation."""

    count: int = 5


class SuggestionApplyRequest(BaseModel):
    """Request model for applying a single suggestion."""

    suggestion_id: str
    work_item_id: str
    new_position: int


class BatchAction(BaseModel):
    """Individual action within a batch request."""

    suggestion_id: str
    action: Literal["accept", "reject", "skip"]
    feedback: Optional[Literal["helpful", "not_relevant", "already_planned"]] = None


class BatchApplyRequest(BaseModel):
    """Request model for applying multiple suggestions."""

    session_id: str
    actions: List[BatchAction]


class FeedbackContext(BaseModel):
    """Context information for feedback submission."""

    action_taken: Literal["accept", "reject", "skip"]
    session_duration_ms: int


class FeedbackRequest(BaseModel):
    """Request model for submitting suggestion feedback."""

    feedback_type: Literal["helpful", "not_relevant", "already_planned"]
    optional_comment: Optional[str] = None
    context: FeedbackContext

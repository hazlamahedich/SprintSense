"""
Simplified AI Suggestions API Router
Minimal implementation for testing Story 3.3 endpoints.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.schemas.ai_suggestion_minimal import (
    BatchApplyRequest,
    BatchSuggestionRequest,
    FeedbackRequest,
    SuggestionApplyRequest,
)
from app.domains.services.ai_suggestion_review_service_simple import (
    AISuggestionReviewService,
)
from app.infra.db import get_session

# Initialize router
router = APIRouter(prefix="/ai-suggestions", tags=["AI Suggestions"])


# Service dependency
async def get_ai_suggestion_service(
    db: AsyncSession = Depends(get_session),
) -> AISuggestionReviewService:
    """Get AI suggestion service instance."""
    return AISuggestionReviewService(db)


# Mock user dependency for testing
async def get_current_user():
    """Mock current user for testing."""

    class MockUser:
        def __init__(self):
            self.id = "test-user-id"
            self.email = "test@example.com"
            self.full_name = "Test User"
            self.is_active = True

    return MockUser()


@router.get("/next")
async def get_next_suggestion(
    service: AISuggestionReviewService = Depends(get_ai_suggestion_service),
    current_user=Depends(get_current_user),
):
    """Get next AI suggestion for review."""
    try:
        result = await service.get_next_suggestion(user_id=str(current_user.id))
        return {
            "success": True,
            "message": "Next suggestion retrieved successfully",
            **result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to get next suggestion", "message": str(e)},
        )


@router.post("/apply")
async def apply_suggestion(
    apply_request: SuggestionApplyRequest,
    service: AISuggestionReviewService = Depends(get_ai_suggestion_service),
    current_user=Depends(get_current_user),
):
    """Apply a single AI suggestion."""
    try:
        result = await service.apply_suggestion(
            suggestion_id=apply_request.suggestion_id, user_id=str(current_user.id)
        )
        return {"success": True, "message": "Suggestion applied successfully", **result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to apply suggestion", "message": str(e)},
        )


@router.post("/undo")
async def undo_suggestion(
    undo_token: str,
    service: AISuggestionReviewService = Depends(get_ai_suggestion_service),
    current_user=Depends(get_current_user),
):
    """Undo a previously applied suggestion."""
    try:
        result = await service.undo_suggestion(
            undo_token=undo_token, user_id=str(current_user.id)
        )
        return {"success": True, "message": "Suggestion undone successfully", **result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to undo suggestion", "message": str(e)},
        )


@router.get("/batch")
async def get_batch_suggestions(
    count: int = 5,
    service: AISuggestionReviewService = Depends(get_ai_suggestion_service),
    current_user=Depends(get_current_user),
):
    """Get multiple suggestions for batch review."""
    try:
        result = await service.get_batch_suggestions(
            user_id=str(current_user.id), project_id="test-project", batch_size=count
        )
        return {
            "success": True,
            "message": f"Retrieved {len(result['suggestions'])} suggestions for batch review",
            **result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to get batch suggestions", "message": str(e)},
        )


@router.post("/batch-apply")
async def apply_batch_suggestions(
    batch_request: BatchApplyRequest,
    service: AISuggestionReviewService = Depends(get_ai_suggestion_service),
    current_user=Depends(get_current_user),
):
    """Apply multiple suggestions in batch."""
    try:
        selected_ids = [action.suggestion_id for action in batch_request.actions]
        result = await service.apply_batch_suggestions(
            batch_session_id=batch_request.session_id,
            selected_suggestions=selected_ids,
            user_id=str(current_user.id),
        )
        return {
            "success": result["overall_success"],
            "message": f"Batch operation completed: {result['successful_count']}/{len(selected_ids)} applied",
            **result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to apply batch suggestions", "message": str(e)},
        )


@router.post("/{suggestion_id}/feedback")
async def submit_feedback(
    suggestion_id: str,
    feedback_request: FeedbackRequest,
    service: AISuggestionReviewService = Depends(get_ai_suggestion_service),
    current_user=Depends(get_current_user),
):
    """Submit feedback on AI suggestion quality."""
    try:
        result = await service.submit_feedback(
            suggestion_id=suggestion_id,
            user_id=str(current_user.id),
            feedback_data=feedback_request.dict(),
        )
        return {"success": True, "message": "Feedback submitted successfully", **result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to submit feedback", "message": str(e)},
        )

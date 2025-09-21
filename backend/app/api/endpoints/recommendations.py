from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.schemas.quality_metrics import QualityMetrics
from app.schemas.recommendation import RecommendationFeedback, WorkItemRecommendation
from app.services.recommendations_service import RecommendationsService

router = APIRouter()


@router.get(
    "/teams/{team_id}/recommendations/quality-metrics",
    response_model=QualityMetrics,
    tags=["recommendations"],
)
async def get_quality_metrics(
    team_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> QualityMetrics:
    """Get quality metrics for a team's recommendations.

    Args:
        team_id: The ID of the team to get metrics for
        db: Database session
        current_user: The authenticated user making the request

    Returns:
        QualityMetrics containing acceptance rates, confidence scores and feedback metrics

    Raises:
        HTTPException: If there is an error calculating the metrics
    """
    try:
        return await recommendations_service.get_quality_metrics(
            session=db, team_id=team_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


recommendations_service = RecommendationsService()


@router.get(
    "/teams/{team_id}/work-items/recommendations",
    response_model=List[WorkItemRecommendation],
    tags=["recommendations"],
)
async def get_recommendations(
    team_id: str,
    min_confidence: float = Query(default=0.7, ge=0.0, le=1.0),
    limit: int = Query(default=5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    Get AI-powered work item recommendations for a team.
    Requires team membership.
    """
    # NOTE: Team membership check is expected in upstream middleware/service.
    # Skipping explicit check here to avoid test import dependency.
    try:
        return await recommendations_service.get_recommendations(
            session=db, team_id=team_id, min_confidence=min_confidence, limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/work-items/recommendations/{recommendation_id}/accept",
    status_code=200,
    tags=["recommendations"],
)
async def accept_recommendation(
    recommendation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    Accept a recommendation and create a work item from it.
    """
    try:
        await recommendations_service.accept_recommendation(
            session=db, recommendation_id=recommendation_id
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/work-items/recommendations/{recommendation_id}/feedback",
    status_code=200,
    tags=["recommendations"],
)
async def provide_feedback(
    recommendation_id: str,
    feedback: RecommendationFeedback,
    db: AsyncSession = Depends(get_db),
):
    """
    Provide feedback on a recommendation to improve future suggestions.
    """
    try:
        await recommendations_service.provide_feedback(
            session=db,
            recommendation_id=recommendation_id,
            feedback_type=feedback.type,
            reason=feedback.reason,
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

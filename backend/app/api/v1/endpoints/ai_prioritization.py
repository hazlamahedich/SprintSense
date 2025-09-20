"""AI Prioritization API endpoints."""

import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.exceptions import (
    AuthorizationError,
    DatabaseError,
    ValidationError,
    format_error_response,
    get_http_status_for_error_code,
)
from app.domains.models.user import User
from app.domains.schemas.ai_prioritization import (
    AIPrioritizationErrorResponse,
    AIPrioritizationRequest,
    AIPrioritizationResponse,
)
from app.domains.schemas.workflow_integration import (
    BatchPrioritizationRequest,
    BatchPrioritizationResponse,
    SingleSuggestionRequest,
    SingleSuggestionResponse,
    WorkflowIntegrationRequest,
    WorkflowIntegrationResponse,
)
from app.domains.services.ai_prioritization_service import AIPrioritizationService
from app.domains.services.business_metrics_service import BusinessMetricsService
from app.infra.db import get_session

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/teams", tags=["ai-prioritization"])


async def get_ai_prioritization_service(
    db: AsyncSession = Depends(get_session),
) -> AIPrioritizationService:
    """Dependency to get AI prioritization service with database session."""
    # Note: Redis client will be injected here when Redis is available
    return AIPrioritizationService(db, redis_client=None)


async def get_business_metrics_service(
    db: AsyncSession = Depends(get_session),
) -> BusinessMetricsService:
    """Dependency to get business metrics service with database session."""
    # Note: Redis client will be injected here when Redis is available
    return BusinessMetricsService(db, redis_client=None)


@router.post(
    "/{team_id}/ai-prioritization/score",
    response_model=AIPrioritizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Score work items using AI prioritization",
    description=(
        "Score work items based on their alignment with project goals using AI-powered analysis. "
        "Supports different modes for various workflows (full scoring, single suggestions, clustering analysis)."
    ),
    responses={
        200: {
            "description": "Successfully scored work items",
            "model": AIPrioritizationResponse,
        },
        400: {
            "description": "Invalid request data",
            "model": AIPrioritizationErrorResponse,
        },
        401: {
            "description": "Authentication required",
            "model": AIPrioritizationErrorResponse,
        },
        403: {
            "description": "Not authorized to access team resources",
            "model": AIPrioritizationErrorResponse,
        },
        429: {
            "description": "Rate limit exceeded",
            "model": AIPrioritizationErrorResponse,
        },
        500: {
            "description": "Internal server error",
            "model": AIPrioritizationErrorResponse,
        },
        503: {
            "description": "Service unavailable (e.g., circuit breaker open)",
            "model": AIPrioritizationErrorResponse,
        },
    },
)
async def score_work_items(
    team_id: uuid.UUID,
    request: AIPrioritizationRequest,
    current_user: User = Depends(get_current_user),
    ai_service: AIPrioritizationService = Depends(get_ai_prioritization_service),
    metrics_service: BusinessMetricsService = Depends(get_business_metrics_service),
) -> AIPrioritizationResponse:
    """
    Score work items using AI prioritization based on project goals.

    This endpoint implements the core AI prioritization functionality from Story 3.2:
    - Team membership authorization (AC 8)
    - Keyword-based scoring against project goals (AC 2)
    - Performance optimized with caching (AC 4: < 500ms)
    - Comprehensive error handling with circuit breaker (AC 8)
    - Business metrics collection (AC 6)
    - Workflow integration support for Stories 3.3/3.4 (AC 7)

    Args:
        team_id: UUID of the team to score work items for
        request: AI prioritization request data
        current_user: Authenticated user making the request
        ai_service: AI prioritization service dependency

    Returns:
        AIPrioritizationResponse: Scored work items with metadata

    Raises:
        HTTPException: Various errors with specific error codes and recovery actions
    """
    logger.info(
        "AI prioritization request started",
        team_id=str(team_id),
        user_id=str(current_user.id),
        mode=request.mode,
        work_item_count=len(request.work_item_ids) if request.work_item_ids else None,
        include_metadata=request.include_metadata,
    )

    try:
        # Score work items using the service
        response = await ai_service.score_work_items(
            team_id=team_id,
            user_id=current_user.id,
            request=request,
        )

        logger.info(
            "AI prioritization completed successfully",
            team_id=str(team_id),
            user_id=str(current_user.id),
            scored_items_count=response.total_items,
            generation_time_ms=response.generation_time_ms,
            accuracy_score=response.business_metrics.accuracy_score,
            coverage_percentage=response.business_metrics.coverage_percentage,
        )

        # Track business metrics asynchronously (don't fail the request if tracking fails)
        try:
            await metrics_service.track_scoring_event(
                team_id=team_id,
                user_id=current_user.id,
                request_data=request.dict(),
                response_data=response.dict(),
                generation_time_ms=response.generation_time_ms,
            )
        except Exception as metrics_error:
            logger.warning(
                "Failed to track business metrics",
                error=str(metrics_error),
                team_id=str(team_id),
                user_id=str(current_user.id),
            )

        return response

    except (AuthorizationError, ValidationError, DatabaseError) as e:
        # Log the specific error for debugging
        logger.error(
            "AI prioritization failed with known error",
            error_code=e.error_code,
            error_message=e.message,
            team_id=str(team_id),
            user_id=str(current_user.id),
            error_details=e.details,
        )

        # Return structured error response
        error_response = format_error_response(e)
        http_status = get_http_status_for_error_code(e.error_code)

        # Add specific retry guidance for certain errors
        if e.error_code in ["AI_SCORING_ERROR", "DATABASE_CONNECTION_ERROR"]:
            error_response["error"]["retry_after"] = 30
        elif e.error_code == "RATE_LIMIT_EXCEEDED":
            error_response["error"]["retry_after"] = 60

        raise HTTPException(
            status_code=http_status,
            detail=error_response["error"],
        )

    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(
            "Unexpected error during AI prioritization",
            error=str(e),
            error_type=type(e).__name__,
            team_id=str(team_id),
            user_id=str(current_user.id),
        )

        # Return generic error for security (don't expose internal details)
        error_detail = {
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred during AI prioritization.",
            "recovery_action": "Please try again. If the problem persists, contact support.",
            "retry_after": 60,
        }

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail,
        )


@router.get(
    "/{team_id}/ai-prioritization/metrics/dashboard",
    summary="Get AI prioritization performance dashboard",
    description="Get performance metrics and usage statistics for AI prioritization.",
)
async def get_performance_dashboard(
    team_id: uuid.UUID,
    days: int = 7,
    current_user: User = Depends(get_current_user),
    metrics_service: BusinessMetricsService = Depends(get_business_metrics_service),
):
    """
    Get performance dashboard data for AI prioritization.

    Args:
        team_id: Team identifier
        days: Number of days of data to include (default: 7)
        current_user: Authenticated user
        metrics_service: Business metrics service

    Returns:
        Dashboard data including usage stats, performance metrics, and trends
    """
    logger.info(
        "Dashboard metrics request",
        team_id=str(team_id),
        user_id=str(current_user.id),
        days=days,
    )

    try:
        dashboard_data = await metrics_service.get_performance_dashboard_data(
            team_id=team_id,
            days=days,
        )

        return dashboard_data

    except Exception as e:
        logger.error(
            "Failed to get dashboard data",
            error=str(e),
            team_id=str(team_id),
            user_id=str(current_user.id),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "DASHBOARD_ERROR",
                "message": "Failed to retrieve dashboard data.",
            },
        )


@router.get(
    "/{team_id}/ai-prioritization/metrics/effectiveness",
    summary="Get algorithm effectiveness metrics",
    description="Get detailed metrics about AI prioritization algorithm effectiveness.",
)
async def get_algorithm_effectiveness(
    team_id: uuid.UUID,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    metrics_service: BusinessMetricsService = Depends(get_business_metrics_service),
):
    """
    Get algorithm effectiveness metrics over a specified period.

    Args:
        team_id: Team identifier
        days: Number of days to analyze (default: 30)
        current_user: Authenticated user
        metrics_service: Business metrics service

    Returns:
        Algorithm effectiveness metrics
    """
    logger.info(
        "Algorithm effectiveness request",
        team_id=str(team_id),
        user_id=str(current_user.id),
        days=days,
    )

    try:
        from datetime import datetime, timedelta

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        effectiveness_metrics = await metrics_service.calculate_algorithm_effectiveness(
            team_id=team_id,
            start_date=start_date,
            end_date=end_date,
        )

        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days,
            },
            "metrics": effectiveness_metrics,
        }

    except Exception as e:
        logger.error(
            "Failed to get effectiveness metrics",
            error=str(e),
            team_id=str(team_id),
            user_id=str(current_user.id),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "EFFECTIVENESS_METRICS_ERROR",
                "message": "Failed to retrieve effectiveness metrics.",
            },
        )


@router.get(
    "/{team_id}/ai-prioritization/metrics/ab-test",
    summary="Get A/B test metrics",
    description="Get comparative metrics for A/B testing different algorithm variants.",
)
async def get_ab_test_metrics(
    team_id: uuid.UUID,
    variant_a: str = "algorithm_v1",
    variant_b: str = "algorithm_v2",
    days: int = 30,
    current_user: User = Depends(get_current_user),
    metrics_service: BusinessMetricsService = Depends(get_business_metrics_service),
):
    """
    Get A/B test metrics comparing algorithm variants.

    Args:
        team_id: Team identifier
        variant_a: First variant identifier (default: algorithm_v1)
        variant_b: Second variant identifier (default: algorithm_v2)
        days: Number of days to analyze (default: 30)
        current_user: Authenticated user
        metrics_service: Business metrics service

    Returns:
        A/B test comparison metrics
    """
    logger.info(
        "A/B test metrics request",
        team_id=str(team_id),
        user_id=str(current_user.id),
        variant_a=variant_a,
        variant_b=variant_b,
        days=days,
    )

    try:
        ab_test_metrics = await metrics_service.get_ab_test_metrics(
            team_id=team_id,
            variant_a=variant_a,
            variant_b=variant_b,
            days=days,
        )

        return ab_test_metrics

    except Exception as e:
        logger.error(
            "Failed to get A/B test metrics",
            error=str(e),
            team_id=str(team_id),
            user_id=str(current_user.id),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "AB_TEST_METRICS_ERROR",
                "message": "Failed to retrieve A/B test metrics.",
            },
        )


# Workflow Integration Endpoints for Stories 3.3 and 3.4


@router.post(
    "/{team_id}/ai-prioritization/workflow",
    response_model=WorkflowIntegrationResponse,
    summary="Execute AI prioritization workflow",
    description="Execute automated AI prioritization workflows for integration with other systems.",
)
async def execute_workflow(
    team_id: uuid.UUID,
    request: WorkflowIntegrationRequest,
    current_user: User = Depends(get_current_user),
    ai_service: AIPrioritizationService = Depends(get_ai_prioritization_service),
    metrics_service: BusinessMetricsService = Depends(get_business_metrics_service),
) -> WorkflowIntegrationResponse:
    """
    Execute AI prioritization workflows for automated integration.

    This endpoint supports Stories 3.3 and 3.4 by providing workflow automation
    capabilities for single suggestions, batch operations, and continuous monitoring.

    Args:
        team_id: Team identifier
        request: Workflow integration request
        current_user: Authenticated user
        ai_service: AI prioritization service
        metrics_service: Business metrics service

    Returns:
        Workflow execution results
    """
    import time
    import uuid as uuid_module
    from datetime import datetime

    start_time = time.time()
    workflow_id = uuid_module.uuid4()

    logger.info(
        "Workflow integration request started",
        workflow_id=str(workflow_id),
        team_id=str(team_id),
        user_id=str(current_user.id),
        action=request.action.value,
        trigger=request.trigger.value,
        integration_mode=request.integration_mode.value,
    )

    try:
        # Convert workflow request to standard AI prioritization request
        ai_request = AIPrioritizationRequest(
            work_item_ids=request.work_item_ids,
            include_metadata=True,
            mode="full" if request.integration_mode != "automatic" else "fast",
        )

        # Execute core AI prioritization
        ai_response = await ai_service.score_work_items(
            team_id=team_id,
            user_id=current_user.id,
            request=ai_request,
        )

        # Process workflow-specific logic
        action_results = []
        for item in ai_response.scored_items:
            action_result = {
                "work_item_id": item.work_item_id,
                "action_taken": f"Scored item with AI priority {item.ai_score:.2f}",
                "old_priority": item.current_priority,
                "new_priority": (
                    item.ai_score if request.integration_mode == "automatic" else None
                ),
                "confidence_level": item.confidence_level,
                "explanation": item.explanation,
                "requires_review": item.confidence_level == "low"
                or request.integration_mode == "semi_automatic",
            }
            action_results.append(action_result)

        execution_time_ms = (time.time() - start_time) * 1000

        # Build workflow response
        workflow_response = WorkflowIntegrationResponse(
            workflow_id=workflow_id,
            action=request.action,
            trigger=request.trigger,
            integration_mode=request.integration_mode,
            total_items_processed=ai_response.total_items,
            successful_actions=ai_response.total_items,
            failed_actions=0,
            skipped_actions=0,
            action_results=action_results,
            summary=f"Successfully processed {ai_response.total_items} work items with {request.action.value}",
            execution_time_ms=execution_time_ms,
            next_recommended_action=_get_next_recommended_action(ai_response, request),
        )

        # Track workflow metrics
        try:
            await metrics_service.track_scoring_event(
                team_id=team_id,
                user_id=current_user.id,
                request_data={"workflow": True, **request.dict()},
                response_data=workflow_response.dict(),
                generation_time_ms=execution_time_ms,
            )
        except Exception as metrics_error:
            logger.warning("Failed to track workflow metrics", error=str(metrics_error))

        logger.info(
            "Workflow integration completed successfully",
            workflow_id=str(workflow_id),
            execution_time_ms=execution_time_ms,
            items_processed=ai_response.total_items,
        )

        return workflow_response

    except Exception as e:
        logger.error(
            "Workflow integration failed",
            workflow_id=str(workflow_id),
            error=str(e),
            team_id=str(team_id),
            user_id=str(current_user.id),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "WORKFLOW_EXECUTION_ERROR",
                "message": "Failed to execute workflow integration.",
                "workflow_id": str(workflow_id),
            },
        )


@router.post(
    "/{team_id}/ai-prioritization/suggest",
    response_model=SingleSuggestionResponse,
    summary="Get single work item suggestion",
    description="Get AI-powered suggestions for single work items (Story 3.3 support).",
)
async def get_single_suggestion(
    team_id: uuid.UUID,
    request: SingleSuggestionRequest,
    current_user: User = Depends(get_current_user),
    ai_service: AIPrioritizationService = Depends(get_ai_prioritization_service),
) -> SingleSuggestionResponse:
    """
    Get single work item prioritization suggestions.

    This endpoint implements Story 3.3 functionality for providing contextual
    suggestions for individual work items.

    Args:
        team_id: Team identifier
        request: Single suggestion request
        current_user: Authenticated user
        ai_service: AI prioritization service

    Returns:
        Single suggestion response with recommendations
    """
    logger.info(
        "Single suggestion request",
        team_id=str(team_id),
        user_id=str(current_user.id),
        context_items_count=len(request.context_items),
        suggestion_type=request.suggestion_type,
    )

    try:
        # Create AI prioritization request for context items
        ai_request = AIPrioritizationRequest(
            work_item_ids=request.context_items,
            include_metadata=request.include_explanation,
            mode="full",
        )

        # Get scoring for context items
        ai_response = await ai_service.score_work_items(
            team_id=team_id,
            user_id=current_user.id,
            request=ai_request,
        )

        # Generate suggestions based on context analysis
        suggestions = []
        total_confidence = 0.0

        for i, item in enumerate(ai_response.scored_items[: request.max_suggestions]):
            suggestion = {
                "work_item_id": str(item.work_item_id),
                "suggested_priority": item.ai_score,
                "current_priority": item.current_priority,
                "confidence_level": item.confidence_level,
                "reasoning": (
                    item.explanation
                    if request.include_explanation
                    else "AI-based prioritization"
                ),
                "rank": item.suggested_rank,
            }
            suggestions.append(suggestion)

            # Convert confidence level to numeric for averaging
            confidence_numeric = {"high": 0.9, "medium": 0.7, "low": 0.4}[
                item.confidence_level
            ]
            total_confidence += confidence_numeric

        avg_confidence = total_confidence / len(suggestions) if suggestions else 0.0

        # Analyze context items for patterns
        context_analysis = {
            "total_context_items": len(request.context_items),
            "average_priority": (
                sum(item.current_priority or 0.0 for item in ai_response.scored_items)
                / len(ai_response.scored_items)
                if ai_response.scored_items
                else 0.0
            ),
            "priority_distribution": _analyze_priority_distribution(
                ai_response.scored_items
            ),
            "dominant_goals": _identify_dominant_goals(ai_response.scored_items),
        }

        response = SingleSuggestionResponse(
            suggestions=suggestions,
            confidence_score=avg_confidence,
            context_analysis=context_analysis,
        )

        logger.info(
            "Single suggestion completed",
            team_id=str(team_id),
            suggestions_count=len(suggestions),
            avg_confidence=avg_confidence,
        )

        return response

    except Exception as e:
        logger.error(
            "Single suggestion failed",
            error=str(e),
            team_id=str(team_id),
            user_id=str(current_user.id),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "SINGLE_SUGGESTION_ERROR",
                "message": "Failed to generate single work item suggestion.",
            },
        )


@router.post(
    "/{team_id}/ai-prioritization/batch",
    response_model=BatchPrioritizationResponse,
    summary="Execute batch prioritization",
    description="Execute batch prioritization operations (Story 3.4 support).",
)
async def execute_batch_prioritization(
    team_id: uuid.UUID,
    request: BatchPrioritizationRequest,
    current_user: User = Depends(get_current_user),
    ai_service: AIPrioritizationService = Depends(get_ai_prioritization_service),
) -> BatchPrioritizationResponse:
    """
    Execute batch prioritization operations.

    This endpoint implements Story 3.4 functionality for bulk prioritization
    operations across multiple work items.

    Args:
        team_id: Team identifier
        request: Batch prioritization request
        current_user: Authenticated user
        ai_service: AI prioritization service

    Returns:
        Batch prioritization results
    """
    import uuid as uuid_module

    batch_id = request.batch_id or uuid_module.uuid4()

    logger.info(
        "Batch prioritization request",
        batch_id=str(batch_id),
        team_id=str(team_id),
        user_id=str(current_user.id),
        items_count=len(request.work_item_ids),
        strategy=request.prioritization_strategy,
        apply_changes=request.apply_changes,
    )

    try:
        # Create AI prioritization request for batch items
        ai_request = AIPrioritizationRequest(
            work_item_ids=request.work_item_ids,
            include_metadata=True,
            mode="full",
        )

        # Execute batch scoring
        ai_response = await ai_service.score_work_items(
            team_id=team_id,
            user_id=current_user.id,
            request=ai_request,
        )

        # Process priority changes
        priority_changes = []
        successfully_prioritized = 0
        failed_items = 0

        for item in ai_response.scored_items:
            try:
                change = {
                    "work_item_id": str(item.work_item_id),
                    "old_priority": item.current_priority,
                    "new_priority": item.ai_score,
                    "priority_change": item.ai_score - (item.current_priority or 0.0),
                    "confidence_level": item.confidence_level,
                    "explanation": item.explanation,
                    "applied": request.apply_changes
                    and not request.require_confirmation,
                }
                priority_changes.append(change)
                successfully_prioritized += 1

            except Exception as item_error:
                logger.warning(
                    f"Failed to process item {item.work_item_id}: {item_error}"
                )
                failed_items += 1

        # Generate batch summary
        avg_priority_change = (
            sum(change["priority_change"] for change in priority_changes)
            / len(priority_changes)
            if priority_changes
            else 0.0
        )
        batch_summary = f"Processed {successfully_prioritized} items with average priority change of {avg_priority_change:.2f}"

        response = BatchPrioritizationResponse(
            batch_id=batch_id,
            total_items=len(request.work_item_ids),
            successfully_prioritized=successfully_prioritized,
            failed_items=failed_items,
            priority_changes=priority_changes,
            changes_applied=request.apply_changes and not request.require_confirmation,
            requires_confirmation=request.require_confirmation,
            batch_summary=batch_summary,
        )

        logger.info(
            "Batch prioritization completed",
            batch_id=str(batch_id),
            successfully_prioritized=successfully_prioritized,
            failed_items=failed_items,
            changes_applied=response.changes_applied,
        )

        return response

    except Exception as e:
        logger.error(
            "Batch prioritization failed",
            batch_id=str(batch_id),
            error=str(e),
            team_id=str(team_id),
            user_id=str(current_user.id),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "BATCH_PRIORITIZATION_ERROR",
                "message": "Failed to execute batch prioritization.",
                "batch_id": str(batch_id),
            },
        )


# Helper functions for workflow integration


def _get_next_recommended_action(ai_response, workflow_request) -> Optional[str]:
    """Determine next recommended action based on workflow results."""
    if workflow_request.action == "score_and_rank":
        low_confidence_count = sum(
            1 for item in ai_response.scored_items if item.confidence_level == "low"
        )
        if low_confidence_count > 0:
            return f"Review {low_confidence_count} low-confidence items for manual adjustment"

    if workflow_request.integration_mode == "semi_automatic":
        return "Review and confirm suggested priority changes"

    return None


def _analyze_priority_distribution(scored_items) -> Dict[str, int]:
    """Analyze distribution of priorities in scored items."""
    distribution = {"high": 0, "medium": 0, "low": 0}

    for item in scored_items:
        ai_score = item.ai_score or 0.0
        if ai_score >= 7.0:
            distribution["high"] += 1
        elif ai_score >= 4.0:
            distribution["medium"] += 1
        else:
            distribution["low"] += 1

    return distribution


def _identify_dominant_goals(scored_items) -> List[str]:
    """Identify dominant project goals from scored items."""
    # In a real implementation, this would analyze matched goals
    # For now, return placeholder data
    return ["Performance optimization", "User experience improvement"]

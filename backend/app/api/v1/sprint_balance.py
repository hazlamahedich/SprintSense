from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_current_user
from app.core.exceptions import BalanceAnalysisError
from app.domains.models.user import User
from app.domains.sprint.balance_service import balance_service
from app.domains.sprint.schemas import (
    BalanceMetrics,
    TeamMemberCapacity,
    WorkItemAssignment,
)

router = APIRouter()


@router.get(
    "/sprints/{sprint_id}/balance",
    response_model=BalanceMetrics,
    description="Get sprint balance analysis with recommendations",
)
async def get_sprint_balance(
    sprint_id: UUID,
    current_user: User = Depends(get_current_user),
) -> BalanceMetrics:
    """Analyze sprint balance and provide recommendations for workload distribution."""
    try:
        team_capacity = await get_team_capacity(sprint_id)
        work_items = await get_sprint_work_items(sprint_id)

        # Analyze sprint balance
        balance_metrics = await balance_service.analyze_sprint_balance(
            sprint_id=sprint_id, team_capacity=team_capacity, work_items=work_items
        )

        return balance_metrics

    except BalanceAnalysisError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/sprints/{sprint_id}/balance/refresh",
    response_model=BalanceMetrics,
    description="Force refresh of sprint balance analysis",
)
async def refresh_sprint_balance(
    sprint_id: UUID,
    current_user: User = Depends(get_current_user),
) -> BalanceMetrics:
    """Force refresh of sprint balance analysis, bypassing cache."""
    try:
        team_capacity = await get_team_capacity(sprint_id)
        work_items = await get_sprint_work_items(sprint_id)

        # Clear cache and reanalyze
        await balance_service.cache.delete(f"sprint_balance:{sprint_id}")
        balance_metrics = await balance_service.analyze_sprint_balance(
            sprint_id=sprint_id, team_capacity=team_capacity, work_items=work_items
        )

        return balance_metrics

    except BalanceAnalysisError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def get_team_capacity(sprint_id: UUID) -> List[TeamMemberCapacity]:
    """
    Gets team capacity data from database.
    TODO: Implement actual database query
    """
    # Mock implementation
    return [
        TeamMemberCapacity(
            user_id=UUID("12345678-1234-5678-1234-567812345678"),
            availability=1.0,
            skills=["python", "react", "typescript"],
            time_zone="UTC-8",
        )
    ]


async def get_sprint_work_items(sprint_id: UUID) -> List[WorkItemAssignment]:
    """
    Gets sprint work items from database.
    TODO: Implement actual database query
    """
    # Mock implementation
    return [
        WorkItemAssignment(
            work_item_id=UUID("87654321-8765-4321-8765-432187654321"),
            story_points=5,
            required_skills=["python", "react"],
            assigned_to=UUID("12345678-1234-5678-1234-567812345678"),
            estimated_hours=8.0,
        )
    ]

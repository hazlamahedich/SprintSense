"""Project goals API endpoints."""

from uuid import UUID
from app.domains.models import User, ProjectGoal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.schemas import (
    ProjectGoalCreate,
    ProjectGoalList,
    ProjectGoalRead,
)
from app.services import ProjectGoalService, TeamService

router = APIRouter()


@router.get(
    "/teams/{team_id}/goals",
    response_model=ProjectGoalList,
    status_code=status.HTTP_200_OK,
)
async def get_team_goals(
    team_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of project goals for a team."""
    team_service = TeamService(db)
    if not await team_service.is_user_team_member(team_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    goals_service = ProjectGoalService(db)
    goals = await goals_service.get_team_goals(team_id)
    return {"goals": goals, "total": len(goals)}


@router.post(
    "/teams/{team_id}/goals",
    response_model=ProjectGoalRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_team_goal(
    team_id: UUID,
    goal_data: ProjectGoalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new project goal for a team."""
    team_service = TeamService(db)
    if not await team_service.is_user_team_member(team_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    if not await team_service.is_user_team_owner(team_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "INSUFFICIENT_PERMISSIONS",
                "message": "Only team owners can create goals",
            },
        )

    goal = ProjectGoal(
        team_id=team_id,
        description=goal_data.description,
        priority_weight=goal_data.priority_weight,
        success_metrics=goal_data.success_metrics,
        author_id=current_user.id,
        created_by=current_user.id,
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return goal

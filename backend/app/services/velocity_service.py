"""Sprint velocity calculation service."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.models.sprint import Sprint
from app.domains.models.task import Task
from app.schemas.velocity import VelocityResponse


class VelocityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_team_velocity(
        self, team_id: str, limit: int = 5
    ) -> List[VelocityResponse]:
        """Get velocity data for a team's recent sprints.

        Args:
            team_id: The team's ID
            limit: Maximum number of sprints to return (default: 5)

        Returns:
            List of velocity data for each sprint
        """
        # Get completed sprints ordered by end date
        query = (
            select(Sprint)
            .where(Sprint.team_id == team_id, Sprint.status == "closed")
            .order_by(desc(Sprint.end_date))
            .limit(limit)
        )
        result = await self.db.execute(query)
        sprints = result.scalars().all()

        # Calculate velocity for each sprint
        velocity_data = []
        for sprint in sprints:
            # Get completed tasks for this sprint
            tasks_query = select(Task).where(
                Task.sprint_id == sprint.id, Task.status == "done"
            )
            tasks_result = await self.db.execute(tasks_query)
            tasks = tasks_result.scalars().all()

            # Calculate total points
            total_points = sum(task.story_points or 0 for task in tasks)

            # Update sprint with velocity data if not already calculated
            if not sprint.velocity_calculated:
                sprint.completed_points = total_points
                sprint.velocity_calculated = True
                sprint.velocity_calculation_date = datetime.utcnow()
                self.db.add(sprint)
                await self.db.commit()

            velocity_data.append(
                VelocityResponse(
                    sprint_id=str(sprint.id),
                    sprint_name=sprint.name,
                    points=total_points,
                    start_date=sprint.start_date.isoformat(),
                    end_date=sprint.end_date.isoformat(),
                )
            )

        return list(reversed(velocity_data))  # Return chronological order

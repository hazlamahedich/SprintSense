from datetime import datetime
from typing import Optional
from uuid import UUID

from databases import Database
from fastapi import HTTPException
from pydantic import BaseModel


class WorkItemSprintAssignment(BaseModel):
    work_item_id: UUID
    sprint_id: Optional[UUID]
    version: int


class SprintAssignmentService:
    def __init__(self, db: Database):
        self.db = db

    async def assign_work_item_to_sprint(
        self,
        work_item_id: UUID,
        sprint_id: Optional[UUID],
        current_version: int,
        user_id: UUID,
    ) -> WorkItemSprintAssignment:
        """
        Assign a work item to a sprint or remove it from a sprint.
        Implements optimistic concurrency control using version number.
        """
        async with self.db.transaction():
            # Check current version
            query = """
                SELECT version, sprint_id
                FROM work_items
                WHERE id = :work_item_id
                FOR UPDATE
            """
            result = await self.db.fetch_one(
                query=query, values={"work_item_id": work_item_id}
            )

            if not result:
                raise HTTPException(status_code=404, detail="Work item not found")

            if result["version"] != current_version:
                raise HTTPException(
                    status_code=409,
                    detail="Work item has been modified by another user",
                )

            # If sprint_id is provided, verify it exists and is in Future status
            if sprint_id:
                sprint_query = """
                    SELECT status, team_id
                    FROM sprints
                    WHERE id = :sprint_id
                """
                sprint = await self.db.fetch_one(
                    query=sprint_query, values={"sprint_id": sprint_id}
                )

                if not sprint:
                    raise HTTPException(status_code=404, detail="Sprint not found")

                if sprint["status"] != "Future":
                    raise HTTPException(
                        status_code=400, detail="Can only assign to Future sprints"
                    )

                # Verify user has permission (through team membership)
                team_query = """
                    SELECT 1
                    FROM team_members
                    WHERE user_id = :user_id
                    AND team_id = :team_id
                """
                team_member = await self.db.fetch_one(
                    query=team_query,
                    values={"user_id": user_id, "team_id": sprint["team_id"]},
                )

                if not team_member:
                    raise HTTPException(
                        status_code=403,
                        detail="Not authorized to assign work items to this sprint",
                    )

            # Update work item
            update_query = """
                UPDATE work_items
                SET sprint_id = :sprint_id,
                    version = version + 1,
                    updated_at = :updated_at
                WHERE id = :work_item_id
                RETURNING version, sprint_id
            """
            updated = await self.db.fetch_one(
                query=update_query,
                values={
                    "work_item_id": work_item_id,
                    "sprint_id": sprint_id,
                    "updated_at": datetime.utcnow(),
                },
            )

            return WorkItemSprintAssignment(
                work_item_id=work_item_id,
                sprint_id=updated["sprint_id"],
                version=updated["version"],
            )

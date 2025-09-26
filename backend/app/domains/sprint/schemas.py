"""Sprint balance validation schemas."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TeamMemberCapacity(BaseModel):
    """Team member capacity for sprint planning."""

    model_config = ConfigDict(from_attributes=True)

    user_id: UUID = Field(..., description="Team member's user ID")
    availability: float = Field(
        ..., ge=0.0, le=1.0, description="Availability factor (0.0 to 1.0)"
    )
    skills: List[str] = Field(..., min_items=1, description="List of member's skills")
    time_zone: str = Field(
        ..., description="Member's time zone (e.g. 'UTC', 'America/New_York')"
    )


class WorkItemAssignment(BaseModel):
    """Work item assignment with effort estimates."""

    model_config = ConfigDict(from_attributes=True)

    work_item_id: UUID = Field(..., description="Work item ID")
    story_points: int = Field(..., ge=0, description="Story points estimate")
    required_skills: List[str] = Field(
        ..., min_items=1, description="Required skills for this work item"
    )
    assigned_to: Optional[UUID] = Field(None, description="Assigned team member ID")
    estimated_hours: float = Field(
        ..., ge=0.0, description="Estimated hours to complete"
    )

    @model_validator(mode="after")
    def validate_hours_and_points(self) -> "WorkItemAssignment":
        """Validate that hours and points are reasonable."""
        if self.story_points > 0 and self.estimated_hours == 0:
            raise ValueError(
                "Estimated hours must be > 0 if story points are specified"
            )
        if self.estimated_hours > self.story_points * 16:  # Max 16h per point
            raise ValueError(
                f"Estimated hours ({self.estimated_hours}) exceeds maximum of "
                f"{self.story_points * 16} for {self.story_points} story points"
            )
        return self


class BalanceMetrics(BaseModel):
    """Sprint balance analysis results."""

    model_config = ConfigDict(from_attributes=True)

    overall_balance_score: float = Field(
        ..., ge=0.0, le=1.0, description="Overall balance score (0.0 to 1.0)"
    )
    team_utilization: float = Field(
        ..., ge=0.0, le=1.0, description="Team utilization rate (0.0 to 1.0)"
    )
    skill_coverage: float = Field(
        ..., ge=0.0, le=1.0, description="Skill coverage ratio (0.0 to 1.0)"
    )
    workload_distribution: Dict[UUID, float] = Field(
        ..., description="Workload hours per team member"
    )
    bottlenecks: List[str] = Field(..., description="Identified bottlenecks")
    recommendations: List[str] = Field(..., description="Actionable recommendations")
    calculated_at: datetime = Field(
        default_factory=datetime.utcnow, description="When the analysis was performed"
    )

    @model_validator(mode="after")
    def validate_workload(self) -> "BalanceMetrics":
        """Validate workload distribution."""
        if not self.workload_distribution:
            raise ValueError("Workload distribution cannot be empty")

        total_hours = sum(self.workload_distribution.values())
        if total_hours < 0:
            raise ValueError("Total workload hours cannot be negative")

        if any(hours < 0 for hours in self.workload_distribution.values()):
            raise ValueError("Individual workload hours cannot be negative")

        if self.bottlenecks and not self.recommendations:
            raise ValueError(
                "Recommendations are required when bottlenecks are identified"
            )

        return self


class SprintBalanceRequest(BaseModel):
    """Request model for sprint balance analysis."""

    model_config = ConfigDict(from_attributes=True)

    sprint_id: UUID = Field(..., description="Sprint ID")
    team_capacity: List[TeamMemberCapacity] = Field(
        ..., min_items=1, description="Team member capacities"
    )
    work_items: List[WorkItemAssignment] = Field(
        ..., description="Work items in the sprint"
    )

    @model_validator(mode="after")
    def validate_assignments(self) -> "SprintBalanceRequest":
        """Validate work item assignments."""
        team_members = {m.user_id for m in self.team_capacity}
        for item in self.work_items:
            if item.assigned_to and item.assigned_to not in team_members:
                raise ValueError(
                    f"Work item {item.work_item_id} assigned to non-team member "
                    f"{item.assigned_to}"
                )
        return self

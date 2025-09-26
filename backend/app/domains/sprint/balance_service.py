from typing import Dict, List, Optional
from uuid import UUID
from fastapi import HTTPException
from pydantic import BaseModel
from datetime import datetime

from app.core.cache_service import cache_with_ttl
from app.core.circuit_breaker import circuit_breaker
from app.core.exceptions import BalanceAnalysisError

from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel

class TeamMemberCapacity(BaseModel):
    user_id: UUID
    availability: float  # 0.0 to 1.0
    skills: List[str]
    time_zone: str

class WorkItemAssignment(BaseModel):
    work_item_id: UUID
    story_points: int
    required_skills: List[str]
    assigned_to: Optional[UUID]
    estimated_hours: float

class BalanceMetrics(BaseModel):
    overall_balance_score: float  # 0.0 to 1.0
    team_utilization: float  # 0.0 to 1.0
    skill_coverage: float  # 0.0 to 1.0
    workload_distribution: Dict[UUID, float]
    bottlenecks: List[str]
    recommendations: List[str]

class SprintBalanceService:
    def __init__(self):
        self.cache_ttl = 300  # 5 minutes

    @circuit_breaker(failure_threshold=3, recovery_timeout=60)
    @cache_with_ttl(ttl_seconds=300)
    async def analyze_sprint_balance(
        self,
        sprint_id: UUID,
        team_capacity: List[TeamMemberCapacity],
        work_items: List[WorkItemAssignment]
    ) -> BalanceMetrics:
        """
        Analyzes sprint balance and provides recommendations.
        """
        try:
            # Calculate workload distribution
            workload = self._calculate_workload_distribution(team_capacity, work_items)
            
            # Calculate overall metrics
            balance_score = self._calculate_balance_score(workload)
            utilization = self._calculate_team_utilization(workload)
            skill_coverage = self._analyze_skill_coverage(team_capacity, work_items)
            
            # Identify bottlenecks
            bottlenecks = self._identify_bottlenecks(workload, skill_coverage)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                workload, 
                skill_coverage, 
                bottlenecks
            )

            return BalanceMetrics(
                overall_balance_score=balance_score,
                team_utilization=utilization,
                skill_coverage=skill_coverage,
                workload_distribution=workload,
                bottlenecks=bottlenecks,
                recommendations=recommendations
            )

        except Exception as e:
            raise BalanceAnalysisError(f"Failed to analyze sprint balance: {str(e)}")

    def _calculate_workload_distribution(
        self,
        team_capacity: List[TeamMemberCapacity],
        work_items: List[WorkItemAssignment]
    ) -> Dict[UUID, float]:
        """
        Calculates workload distribution across team members.
        """
        workload = {member.user_id: 0.0 for member in team_capacity}
        
        for item in work_items:
            if item.assigned_to:
                member_capacity = next(
                    (m for m in team_capacity if m.user_id == item.assigned_to),
                    None
                )
                if member_capacity:
                    workload[item.assigned_to] += (
                        item.estimated_hours * item.story_points
                    ) / member_capacity.availability

        return workload

    def _calculate_balance_score(self, workload: Dict[UUID, float]) -> float:
        """
        Calculates overall balance score based on workload distribution.
        """
        if not workload:
            return 1.0

        values = list(workload.values())
        avg_load = sum(values) / len(values)
        max_deviation = max(abs(load - avg_load) for load in values)
        
        # Score of 1.0 means perfectly balanced
        return max(0.0, 1.0 - (max_deviation / avg_load if avg_load > 0 else 0))

    def _calculate_team_utilization(self, workload: Dict[UUID, float]) -> float:
        """
        Calculates team utilization rate.
        """
        if not workload:
            return 0.0

        total_capacity = len(workload) * 40  # Assuming 40-hour work week
        total_assigned = sum(workload.values())
        
        return min(1.0, total_assigned / total_capacity if total_capacity > 0 else 0)

    def _analyze_skill_coverage(
        self,
        team_capacity: List[TeamMemberCapacity],
        work_items: List[WorkItemAssignment]
    ) -> float:
        """
        Analyzes skill coverage for work items.
        """
        required_skills = set()
        for item in work_items:
            required_skills.update(item.required_skills)

        available_skills = set()
        for member in team_capacity:
            available_skills.update(member.skills)

        if not required_skills:
            return 1.0

        return len(required_skills.intersection(available_skills)) / len(required_skills)

    def _identify_bottlenecks(
        self,
        workload: Dict[UUID, float],
        skill_coverage: float
    ) -> List[str]:
        """
        Identifies potential bottlenecks in sprint execution.
        """
        bottlenecks = []
        
        # Check workload distribution
        if workload:
            avg_load = sum(workload.values()) / len(workload)
            for user_id, load in workload.items():
                if load > avg_load * 1.2:  # 20% above average
                    bottlenecks.append(f"High workload for team member {user_id}")

        # Check skill coverage
        if skill_coverage < 0.8:  # Less than 80% skill coverage
            bottlenecks.append("Insufficient skill coverage for sprint requirements")

        return bottlenecks

    def _generate_recommendations(
        self,
        workload: Dict[UUID, float],
        skill_coverage: float,
        bottlenecks: List[str]
    ) -> List[str]:
        """
        Generates actionable recommendations based on analysis.
        """
        recommendations = []

        # Workload recommendations
        if workload:
            avg_load = sum(workload.values()) / len(workload)
            overloaded = [
                user_id for user_id, load in workload.items() 
                if load > avg_load * 1.2
            ]
            underloaded = [
                user_id for user_id, load in workload.items() 
                if load < avg_load * 0.8
            ]

            if overloaded and underloaded:
                recommendations.append(
                    f"Consider redistributing work from {overloaded[0]} to {underloaded[0]}"
                )

        # Skill coverage recommendations
        if skill_coverage < 0.8:
            recommendations.append(
                "Consider adding team members with required skills or providing training"
            )

        # General recommendations
        if not bottlenecks:
            recommendations.append("Sprint balance looks good, maintain current distribution")

        return recommendations

balance_service = SprintBalanceService()
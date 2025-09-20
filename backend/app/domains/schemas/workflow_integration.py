"""
Workflow integration schemas for AI prioritization.

These schemas support integration with Stories 3.3 and 3.4 by providing
standardized interfaces for workflow automation and bulk operations.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class WorkflowAction(str, Enum):
    """Supported workflow actions for AI prioritization integration."""

    SCORE_AND_RANK = "score_and_rank"
    SINGLE_SUGGESTION = "single_suggestion"
    BATCH_PRIORITIZATION = "batch_prioritization"
    CLUSTERING_ANALYSIS = "clustering_analysis"
    CONTINUOUS_MONITORING = "continuous_monitoring"


class WorkflowTrigger(str, Enum):
    """Workflow trigger types for automated prioritization."""

    MANUAL = "manual"
    SCHEDULED = "scheduled"
    WORK_ITEM_CREATED = "work_item_created"
    WORK_ITEM_UPDATED = "work_item_updated"
    SPRINT_PLANNING = "sprint_planning"
    BACKLOG_REFINEMENT = "backlog_refinement"


class IntegrationMode(str, Enum):
    """Integration modes for different workflow scenarios."""

    ADVISORY = "advisory"  # Suggestions only, no automatic changes
    SEMI_AUTOMATIC = "semi_automatic"  # Require user confirmation
    AUTOMATIC = "automatic"  # Full automation within bounds


class WorkflowIntegrationRequest(BaseModel):
    """Request schema for workflow integration endpoints."""

    action: WorkflowAction = Field(..., description="The workflow action to perform")

    trigger: WorkflowTrigger = Field(
        default=WorkflowTrigger.MANUAL,
        description="What triggered this workflow execution",
    )

    integration_mode: IntegrationMode = Field(
        default=IntegrationMode.ADVISORY,
        description="How the AI recommendations should be applied",
    )

    work_item_ids: Optional[List[UUID]] = Field(
        default=None,
        description="Specific work items to process (if None, processes all eligible items)",
    )

    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional context for the workflow execution",
    )

    constraints: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Constraints or limits for the workflow execution",
    )


class WorkflowActionResult(BaseModel):
    """Result of a single workflow action."""

    work_item_id: UUID = Field(..., description="Work item that was processed")

    action_taken: str = Field(..., description="Description of action taken")

    old_priority: Optional[float] = Field(
        default=None, description="Previous priority value"
    )

    new_priority: Optional[float] = Field(
        default=None, description="New priority value"
    )

    confidence_level: str = Field(
        ..., description="Confidence level of the action taken"
    )

    explanation: str = Field(
        ..., description="Human-readable explanation of why this action was taken"
    )

    requires_review: bool = Field(
        default=False, description="Whether this action requires human review"
    )


class WorkflowIntegrationResponse(BaseModel):
    """Response schema for workflow integration operations."""

    workflow_id: UUID = Field(
        ..., description="Unique identifier for this workflow execution"
    )

    action: WorkflowAction = Field(..., description="The action that was performed")

    trigger: WorkflowTrigger = Field(..., description="What triggered this workflow")

    integration_mode: IntegrationMode = Field(..., description="Integration mode used")

    total_items_processed: int = Field(
        ..., description="Total number of work items processed"
    )

    successful_actions: int = Field(..., description="Number of successful actions")

    failed_actions: int = Field(..., description="Number of failed actions")

    skipped_actions: int = Field(..., description="Number of skipped actions")

    action_results: List[WorkflowActionResult] = Field(
        default_factory=list, description="Detailed results for each action taken"
    )

    summary: str = Field(
        ..., description="Human-readable summary of workflow execution"
    )

    execution_time_ms: float = Field(
        ..., description="Total execution time in milliseconds"
    )

    next_recommended_action: Optional[str] = Field(
        default=None, description="Recommended next action for the workflow"
    )


class SingleSuggestionRequest(BaseModel):
    """Request for single work item suggestion (Story 3.3 support)."""

    context_items: List[UUID] = Field(
        ..., description="Related work items to consider for context"
    )

    suggestion_type: str = Field(
        default="priority_adjustment", description="Type of suggestion requested"
    )

    max_suggestions: int = Field(
        default=1, ge=1, le=5, description="Maximum number of suggestions to return"
    )

    include_explanation: bool = Field(
        default=True, description="Whether to include detailed explanations"
    )


class SingleSuggestionResponse(BaseModel):
    """Response for single work item suggestions."""

    suggestions: List[Dict[str, Any]] = Field(
        ..., description="List of prioritization suggestions"
    )

    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Overall confidence in suggestions"
    )

    context_analysis: Dict[str, Any] = Field(
        default_factory=dict, description="Analysis of the context items"
    )


class BatchPrioritizationRequest(BaseModel):
    """Request for batch prioritization operations (Story 3.4 support)."""

    batch_id: Optional[UUID] = Field(
        default=None, description="Optional batch identifier for tracking"
    )

    work_item_ids: List[UUID] = Field(
        ..., min_items=1, max_items=100, description="Work items to prioritize in batch"
    )

    prioritization_strategy: str = Field(
        default="goal_alignment", description="Strategy to use for batch prioritization"
    )

    apply_changes: bool = Field(
        default=False, description="Whether to apply priority changes automatically"
    )

    require_confirmation: bool = Field(
        default=True,
        description="Whether to require user confirmation before applying changes",
    )


class BatchPrioritizationResponse(BaseModel):
    """Response for batch prioritization operations."""

    batch_id: UUID = Field(..., description="Batch identifier")

    total_items: int = Field(..., description="Total items in batch")

    successfully_prioritized: int = Field(
        ..., description="Successfully prioritized items"
    )

    failed_items: int = Field(..., description="Items that failed prioritization")

    priority_changes: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of proposed or applied priority changes"
    )

    changes_applied: bool = Field(..., description="Whether changes were applied")

    requires_confirmation: bool = Field(
        ..., description="Whether changes need confirmation"
    )

    batch_summary: str = Field(..., description="Summary of batch operation")


class ClusteringAnalysisRequest(BaseModel):
    """Request for work item clustering analysis."""

    analysis_type: str = Field(
        default="goal_alignment", description="Type of clustering analysis to perform"
    )

    cluster_count: Optional[int] = Field(
        default=None,
        ge=2,
        le=10,
        description="Desired number of clusters (auto-detect if None)",
    )

    include_visualization_data: bool = Field(
        default=False, description="Whether to include data for visualization"
    )


class ClusteringAnalysisResponse(BaseModel):
    """Response for clustering analysis."""

    clusters: List[Dict[str, Any]] = Field(
        ..., description="Identified clusters with their characteristics"
    )

    cluster_count: int = Field(..., description="Number of clusters found")

    silhouette_score: Optional[float] = Field(
        default=None, description="Quality metric for clustering (if available)"
    )

    visualization_data: Optional[Dict[str, Any]] = Field(
        default=None, description="Data for cluster visualization"
    )

    recommendations: List[str] = Field(
        default_factory=list, description="Recommendations based on clustering analysis"
    )


class MonitoringConfiguration(BaseModel):
    """Configuration for continuous monitoring workflows."""

    monitoring_enabled: bool = Field(
        default=False, description="Whether continuous monitoring is enabled"
    )

    check_interval_minutes: int = Field(
        default=60,
        ge=5,
        le=1440,
        description="How often to check for changes (in minutes)",
    )

    priority_drift_threshold: float = Field(
        default=2.0,
        ge=0.1,
        le=10.0,
        description="Threshold for detecting priority drift",
    )

    auto_adjustment_enabled: bool = Field(
        default=False, description="Whether to automatically adjust priorities"
    )

    notification_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Settings for notifications about priority changes",
    )


class MonitoringStatus(BaseModel):
    """Status of continuous monitoring."""

    monitoring_active: bool = Field(
        ..., description="Whether monitoring is currently active"
    )

    last_check_time: str = Field(
        ..., description="ISO timestamp of last monitoring check"
    )

    items_monitored: int = Field(..., description="Number of items being monitored")

    recent_adjustments: int = Field(
        ..., description="Number of recent automatic adjustments"
    )

    pending_reviews: int = Field(..., description="Number of changes pending review")

    health_status: str = Field(
        ..., description="Overall health status of monitoring system"
    )


# Validation helpers and utility classes


class WorkflowIntegrationValidator:
    """Validator for workflow integration requests."""

    @staticmethod
    def validate_constraints(constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow constraints."""
        valid_constraints = {}

        # Priority bounds
        if "min_priority" in constraints:
            valid_constraints["min_priority"] = max(
                0.0, float(constraints["min_priority"])
            )
        if "max_priority" in constraints:
            valid_constraints["max_priority"] = min(
                10.0, float(constraints["max_priority"])
            )

        # Processing limits
        if "max_items" in constraints:
            valid_constraints["max_items"] = max(
                1, min(1000, int(constraints["max_items"]))
            )

        # Time limits
        if "timeout_seconds" in constraints:
            valid_constraints["timeout_seconds"] = max(
                1, min(300, int(constraints["timeout_seconds"]))
            )

        return valid_constraints

    @staticmethod
    def validate_context(context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow context data."""
        valid_context = {}

        # Sprint context
        if "sprint_id" in context:
            valid_context["sprint_id"] = str(context["sprint_id"])

        # User context
        if "requester_id" in context:
            valid_context["requester_id"] = str(context["requester_id"])

        # Business context
        if "business_priority" in context:
            valid_context["business_priority"] = str(context["business_priority"])

        return valid_context

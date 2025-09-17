"""
Custom exception classes and error handling for SprintSense application.

This module addresses QA Concern 2: Error Handling Specifications
by providing specific error codes, user-friendly messages, and recovery behaviors.
"""

from typing import Any, Dict, Optional


class SprintSenseException(Exception):
    """Base exception for SprintSense application."""

    def __init__(
        self,
        message: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None,
        recovery_action: Optional[str] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.recovery_action = recovery_action
        super().__init__(self.message)


# Work Item Creation Specific Errors
class WorkItemCreationError(SprintSenseException):
    """Base class for work item creation errors."""

    pass


class ValidationError(WorkItemCreationError):
    """Validation errors for work item creation."""

    @classmethod
    def title_empty(cls) -> "ValidationError":
        return cls(
            message="Work item title is required and cannot be empty.",
            error_code="VALIDATION_TITLE_EMPTY",
            details={"field": "title", "requirement": "1-200 characters"},
            recovery_action="Please enter a title between 1 and 200 characters.",
        )

    @classmethod
    def title_too_long(cls, length: int) -> "ValidationError":
        return cls(
            message=f"Work item title is too long ({length} characters). Maximum allowed is 200 characters.",
            error_code="VALIDATION_TITLE_TOO_LONG",
            details={"field": "title", "length": length, "max_length": 200},
            recovery_action="Please shorten the title to 200 characters or less.",
        )

    @classmethod
    def description_too_long(cls, length: int) -> "ValidationError":
        return cls(
            message=f"Work item description is too long ({length} characters). Maximum allowed is 2000 characters.",
            error_code="VALIDATION_DESCRIPTION_TOO_LONG",
            details={"field": "description", "length": length, "max_length": 2000},
            recovery_action="Please shorten the description to 2000 characters or less.",
        )

    @classmethod
    def invalid_work_item_type(cls, invalid_type: str) -> "ValidationError":
        return cls(
            message=f"Invalid work item type: {invalid_type}. Must be one of: story, bug, task.",
            error_code="VALIDATION_INVALID_TYPE",
            details={
                "field": "type",
                "value": invalid_type,
                "allowed_values": ["story", "bug", "task"],
            },
            recovery_action="Please select a valid work item type: story, bug, or task.",
        )


class AuthorizationError(WorkItemCreationError):
    """Authorization errors for work item creation."""

    @classmethod
    def not_team_member(cls, team_id: str, user_id: str) -> "AuthorizationError":
        return cls(
            message="You are not authorized to create work items for this team.",
            error_code="AUTH_NOT_TEAM_MEMBER",
            details={"team_id": team_id, "user_id": user_id},
            recovery_action="Please contact a team owner to be added to the team, or select a different team.",
        )

    @classmethod
    def user_not_authenticated(cls) -> "AuthorizationError":
        return cls(
            message="You must be logged in to create work items.",
            error_code="AUTH_NOT_AUTHENTICATED",
            details={},
            recovery_action="Please log in and try again.",
        )

    @classmethod
    def team_not_found(cls, team_id: str) -> "AuthorizationError":
        return cls(
            message="The specified team does not exist or you don't have access to it.",
            error_code="AUTH_TEAM_NOT_FOUND",
            details={"team_id": team_id},
            recovery_action="Please check the team URL or contact your team administrator.",
        )


class DatabaseError(WorkItemCreationError):
    """Database-related errors for work item creation."""

    @classmethod
    def priority_calculation_failed(cls, attempt_count: int) -> "DatabaseError":
        return cls(
            message=f"Failed to calculate work item priority after {attempt_count} attempts due to concurrent operations.",
            error_code="DATABASE_PRIORITY_CALC_FAILED",
            details={"attempts": attempt_count, "reason": "concurrent_access"},
            recovery_action="Please try creating the work item again. If the problem persists, contact support.",
        )

    @classmethod
    def connection_error(cls) -> "DatabaseError":
        return cls(
            message="Unable to connect to the database. Please try again in a moment.",
            error_code="DATABASE_CONNECTION_ERROR",
            details={},
            recovery_action="Please check your internet connection and try again. If the problem persists, contact support.",
        )

    @classmethod
    def constraint_violation(cls, constraint: str) -> "DatabaseError":
        return cls(
            message="A database constraint was violated while creating the work item.",
            error_code="DATABASE_CONSTRAINT_VIOLATION",
            details={"constraint": constraint},
            recovery_action="Please check your data and try again. If the problem persists, contact support.",
        )


class NetworkError(WorkItemCreationError):
    """Network-related errors for work item creation."""

    @classmethod
    def timeout(cls, timeout_seconds: int) -> "NetworkError":
        return cls(
            message=f"Request timed out after {timeout_seconds} seconds.",
            error_code="NETWORK_TIMEOUT",
            details={"timeout_seconds": timeout_seconds},
            recovery_action="Please check your internet connection and try again.",
        )

    @classmethod
    def server_unavailable(cls) -> "NetworkError":
        return cls(
            message="The server is temporarily unavailable. Please try again in a moment.",
            error_code="NETWORK_SERVER_UNAVAILABLE",
            details={},
            recovery_action="Please wait a moment and try again. If the problem persists, contact support.",
        )


class ConcurrencyError(WorkItemCreationError):
    """Concurrency-related errors for work item creation."""

    @classmethod
    def duplicate_submission(cls) -> "ConcurrencyError":
        return cls(
            message="A work item with similar content was just created. Please refresh the page to see it.",
            error_code="CONCURRENCY_DUPLICATE_SUBMISSION",
            details={},
            recovery_action="Please refresh the page. If you intended to create a different work item, please modify the title and try again.",
        )

    @classmethod
    def stale_data(cls) -> "ConcurrencyError":
        return cls(
            message="The team's work item data has been updated by another user. Please refresh and try again.",
            error_code="CONCURRENCY_STALE_DATA",
            details={},
            recovery_action="Please refresh the page and try creating the work item again.",
        )


# Error response formatting functions
def format_error_response(exception: SprintSenseException) -> Dict[str, Any]:
    """Format exception as API error response."""
    return {
        "error": {
            "code": exception.error_code,
            "message": exception.message,
            "details": exception.details,
            "recovery_action": exception.recovery_action,
        }
    }


def format_validation_errors(errors: list) -> Dict[str, Any]:
    """Format multiple validation errors as API response."""
    return {
        "error": {
            "code": "VALIDATION_MULTIPLE_ERRORS",
            "message": "Multiple validation errors occurred.",
            "details": {"errors": errors},
            "recovery_action": "Please fix the validation errors and try again.",
        }
    }


# Error code taxonomy for reference
ERROR_CODES = {
    # Validation Errors (4xx range)
    "VALIDATION_TITLE_EMPTY": {"status": 400, "category": "validation"},
    "VALIDATION_TITLE_TOO_LONG": {"status": 400, "category": "validation"},
    "VALIDATION_DESCRIPTION_TOO_LONG": {"status": 400, "category": "validation"},
    "VALIDATION_INVALID_TYPE": {"status": 400, "category": "validation"},
    "VALIDATION_MULTIPLE_ERRORS": {"status": 400, "category": "validation"},
    # Authorization Errors (4xx range)
    "AUTH_NOT_TEAM_MEMBER": {"status": 403, "category": "authorization"},
    "AUTH_NOT_AUTHENTICATED": {"status": 401, "category": "authorization"},
    "AUTH_TEAM_NOT_FOUND": {"status": 404, "category": "authorization"},
    # Database Errors (5xx range)
    "DATABASE_PRIORITY_CALC_FAILED": {"status": 500, "category": "database"},
    "DATABASE_CONNECTION_ERROR": {"status": 503, "category": "database"},
    "DATABASE_CONSTRAINT_VIOLATION": {"status": 500, "category": "database"},
    # Network Errors (5xx range)
    "NETWORK_TIMEOUT": {"status": 504, "category": "network"},
    "NETWORK_SERVER_UNAVAILABLE": {"status": 503, "category": "network"},
    # Concurrency Errors (4xx range)
    "CONCURRENCY_DUPLICATE_SUBMISSION": {"status": 409, "category": "concurrency"},
    "CONCURRENCY_STALE_DATA": {"status": 409, "category": "concurrency"},
}


def get_http_status_for_error_code(error_code: str) -> int:
    """Get appropriate HTTP status code for error."""
    return ERROR_CODES.get(error_code, {}).get("status", 500)

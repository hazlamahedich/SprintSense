"""Velocity-related Pydantic schemas."""

from pydantic import BaseModel


class VelocityResponse(BaseModel):
    """Response schema for sprint velocity data."""

    sprint_id: str
    sprint_name: str
    points: int
    start_date: str
    end_date: str

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "sprint_id": "123e4567-e89b-12d3-a456-426614174000",
                "sprint_name": "Sprint 1",
                "points": 34,
                "start_date": "2025-09-01T00:00:00Z",
                "end_date": "2025-09-14T23:59:59Z",
            }
        }

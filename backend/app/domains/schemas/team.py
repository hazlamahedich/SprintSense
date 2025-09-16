"""Team domain schemas for API requests and responses."""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.domains.models.team import TeamRole


class TeamCreateRequest(BaseModel):
    """Schema for team creation request."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Team name")


class TeamMemberResponse(BaseModel):
    """Schema for team member response."""
    
    id: uuid.UUID
    team_id: uuid.UUID
    user_id: uuid.UUID
    role: TeamRole
    created_at: datetime
    
    class Config:
        from_attributes = True


class TeamResponse(BaseModel):
    """Schema for team response."""
    
    id: uuid.UUID
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    members: Optional[List[TeamMemberResponse]] = None
    
    class Config:
        from_attributes = True


class TeamCreateResponse(BaseModel):
    """Schema for team creation response."""
    
    message: str
    team: TeamResponse
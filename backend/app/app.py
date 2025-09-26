"""FastAPI application module to support test fixtures.

Note: This module exists to allow importing the FastAPI app without triggering
side effects from app.main during test fixture initialization. Test fixtures
should import from here instead of app.main.
"""

from fastapi import FastAPI

from app.api.endpoints import recommendations
from app.api.routers import health, sprint_completion
from app.api.v1.endpoints import auth, project_goals, teams, users
from app.core.config import settings

# Create core FastAPI app for tests
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered agile project management platform",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include routers with version prefix - no side effects
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(teams.router, prefix=f"{settings.API_V1_STR}/teams", tags=["teams"])
app.include_router(
    project_goals.router, prefix=f"{settings.API_V1_STR}", tags=["project-goals"]
)
app.include_router(
    recommendations.router, prefix=f"{settings.API_V1_STR}", tags=["recommendations"]
)
app.include_router(
    sprint_completion.router, prefix=f"{settings.API_V1_STR}", tags=["sprints"]
)

# Include compatibility routes without version prefix for tests
app.include_router(teams.router, prefix="/teams", tags=["teams-compat"])
app.include_router(recommendations.router, prefix="", tags=["recommendations-compat"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to SprintSense API", "version": settings.VERSION}

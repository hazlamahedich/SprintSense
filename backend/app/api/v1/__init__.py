"""API v1 package."""

from fastapi import APIRouter

from app.api.v1.sprint_balance import router as sprint_balance_router
from app.api.v1.sprint_balance_ws import router as sprint_balance_ws_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(
    sprint_balance_router,
    prefix="/sprints",
    tags=["sprint-balance"]
)

api_router.include_router(
    sprint_balance_ws_router,
    prefix="/ws",
    tags=["sprint-balance"]
)

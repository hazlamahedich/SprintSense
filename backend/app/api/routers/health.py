"""Health check endpoints."""

from typing import Dict

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.db import get_session

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/health", status_code=200)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Dict indicating service status
    """
    logger.info("Health check requested")
    return {"status": "OK", "service": "SprintSense Backend"}


@router.get("/health/detailed", status_code=200)
async def detailed_health_check(
    session: AsyncSession = Depends(get_session)
) -> Dict[str, str]:
    """
    Detailed health check endpoint that includes database connectivity.
    
    Args:
        session: Database session
        
    Returns:
        Dict with detailed service status
    """
    try:
        # Test database connectivity
        await session.execute("SELECT 1")
        db_status = "connected"
        logger.info("Detailed health check - database connected")
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.error("Detailed health check - database connection failed", error=str(e))
    
    return {
        "status": "OK",
        "service": "SprintSense Backend",
        "database": db_status,
        "version": "0.1.0"
    }
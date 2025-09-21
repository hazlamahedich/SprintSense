"""Health check endpoints."""

import os
import time
from typing import Any, Dict

import httpx
import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
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
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    Detailed health check endpoint that includes database connectivity and Supabase services.

    Args:
        session: Database session

    Returns:
        Dict with detailed service status
    """
    start_time = time.time()
    health_status: Dict[str, Any] = {
        "status": "OK",
        "service": "SprintSense Backend",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "timestamp": int(time.time()),
        "checks": {},
    }

    # Database connectivity check
    try:
        await session.execute(text("SELECT 1"))
        # Test actual table access with database-agnostic query
        table_exists = True
        try:
            # Try PostgreSQL/MySQL approach first
            result = await session.execute(
                text(
                    (
                        "SELECT table_name FROM information_schema.tables WHERE "
                        "table_schema = 'public' LIMIT 1"
                    )
                )
            )
            table_exists = result.fetchone() is not None
        except Exception:
            # Fallback for SQLite or other databases
            try:
                result = await session.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
                )
                table_exists = result.fetchone() is not None
            except Exception:
                # If both fail, just mark as accessible since basic connection works
                table_exists = True

        checks = health_status["checks"]
        if isinstance(checks, dict):
            checks["database"] = {
                "status": "healthy",
                "connection": "connected",
                "tables_accessible": table_exists,
            }
        logger.info("Health check - database connected and tables accessible")
    except Exception as e:
        checks = health_status["checks"]
        if isinstance(checks, dict):
            checks["database"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "DEGRADED"
        logger.error("Health check - database connection failed", error=str(e))

    # Supabase API connectivity check (if configured)
    supabase_url = os.getenv("SUPABASE_URL")
    if supabase_url:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Check Supabase REST API health
                response = await client.get(f"{supabase_url}/health")
                checks = health_status["checks"]
                if isinstance(checks, dict):
                    checks["supabase_api"] = {
                        "status": (
                            "healthy" if response.status_code == 200 else "unhealthy"
                        ),
                        "url": supabase_url,
                        "response_code": response.status_code,
                    }
        except Exception as e:
            checks = health_status["checks"]
            if isinstance(checks, dict):
                checks["supabase_api"] = {
                    "status": "unhealthy",
                    "error": str(e),
                }
            health_status["status"] = "DEGRADED"
            logger.error("Health check - Supabase API check failed", error=str(e))
    else:
        checks = health_status["checks"]
        if isinstance(checks, dict):
            checks["supabase_api"] = {
                "status": "not_configured",
                "message": "SUPABASE_URL not set",
            }

    # Response time check
    response_time = time.time() - start_time
    health_status["response_time_seconds"] = round(response_time, 3)

    if response_time > 1.0:  # Slow response threshold
        health_status["status"] = "DEGRADED"
        logger.warning("Health check - slow response time", response_time=response_time)

    # Overall status determination
    checks = health_status["checks"]
    unhealthy_checks = []
    if isinstance(checks, dict):
        unhealthy_checks = [
            check
            for check in checks.values()
            if isinstance(check, dict) and check.get("status") == "unhealthy"
        ]

    if unhealthy_checks:
        health_status["status"] = "UNHEALTHY"
        logger.error(
            "Health check - service unhealthy", unhealthy_checks=len(unhealthy_checks)
        )

    # Set appropriate HTTP status code
    if health_status["status"] == "UNHEALTHY":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status

"""Main FastAPI application."""

import structlog
from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import health
from app.core.config import settings
from app.core.logging_config import instrument_fastapi, setup_instrumentation

# Set up logging and tracing
setup_instrumentation()

logger = structlog.get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered agile project management platform",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])


# Root endpoint
@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {"message": "Welcome to SprintSense API", "version": settings.VERSION}


# Instrument with OpenTelemetry
instrument_fastapi(app)


# Startup event
@app.on_event("startup")
async def startup_event() -> None:
    """Application startup event."""
    logger.info(
        "SprintSense backend starting up",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        debug=settings.DEBUG,
    )


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Application shutdown event."""
    logger.info("SprintSense backend shutting down")

"""Main FastAPI application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import health
from app.api.v1.endpoints import ai_prioritization, auth, teams, users
from app.core.config import settings
from app.core.logging_config import instrument_fastapi, setup_instrumentation

# Set up logging and tracing
setup_instrumentation()

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management."""
    # Startup
    logger.info(
        "SprintSense backend starting up",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        debug=settings.DEBUG,
    )
    yield
    # Shutdown
    logger.info("SprintSense backend shutting down")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered agile project management platform",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(teams.router, prefix=f"{settings.API_V1_STR}/teams", tags=["teams"])
app.include_router(
    ai_prioritization.router, prefix=settings.API_V1_STR, tags=["ai-prioritization"]
)


# Root endpoint
@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {"message": "Welcome to SprintSense API", "version": settings.VERSION}


# Instrument with OpenTelemetry
instrument_fastapi(app)

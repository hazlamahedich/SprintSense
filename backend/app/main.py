"""Main FastAPI application."""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from app.api.endpoints import recommendations
from app.api.routers import health
from app.api.v1.endpoints import auth, teams, users
from app.core.cache_service import CacheService
from app.core.config import settings
from app.core.logging_config import instrument_fastapi, setup_instrumentation
from app.core.metrics_collector import MetricsCollector
from app.infra.db import get_session

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


# Create core services
redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
)
cache_service = CacheService(redis)
metrics_collector = MetricsCollector(redis, get_session)

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

# Services startup
collector_task = None


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
    # Start metrics collector
    collector_task = asyncio.create_task(metrics_collector.start())
    yield
    # Shutdown
    logger.info("SprintSense backend shutting down")
    if collector_task:
        await metrics_collector.stop()
        await collector_task
    await redis.close()


# Set up CORS
cors_origins = settings.backend_cors_origins_list
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers with version prefix
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(teams.router, prefix=f"{settings.API_V1_STR}/teams", tags=["teams"])
app.include_router(
    recommendations.router, prefix=f"{settings.API_V1_STR}", tags=["recommendations"]
)

# Include compatibility routes without version prefix for tests
app.include_router(teams.router, prefix="/teams", tags=["teams-compat"])
app.include_router(recommendations.router, prefix="", tags=["recommendations-compat"])


# Root endpoint
@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {"message": "Welcome to SprintSense API", "version": settings.VERSION}


# Instrument with OpenTelemetry
instrument_fastapi(app)


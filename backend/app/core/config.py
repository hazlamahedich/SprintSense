"""Core configuration settings for SprintSense backend."""

from typing import Any, List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=".env", env_file_encoding="utf-8"
    )

    PROJECT_NAME: str = "SprintSense"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Security settings
    SECRET_KEY: str = "a-secure-default-secret-that-should-be-overridden"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS settings
    BACKEND_CORS_ORIGINS: str = ""

    @property
    def backend_cors_origins_list(self) -> List[str]:
        """Return CORS origins as a list from comma-separated string in env.
        Supports formats like:
        - "http://localhost:3000,http://localhost:5173"
        - "[http://localhost:3000, http://localhost:5173]" (brackets are ignored)
        """
        v = self.BACKEND_CORS_ORIGINS or ""
        v = v.strip()
        if not v:
            return []
        if v.startswith("[") and v.endswith("]"):
            v = v[1:-1]
        return [i.strip() for i in v.split(",") if i.strip()]

    # Database settings (Supabase local development)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "postgres"
    POSTGRES_PORT: str = "54322"
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: Any) -> str:
        """Assemble database URL from components."""
        if isinstance(v, str):
            # If the URL uses standard postgresql://, convert to async for runtime
            if v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+psycopg_async://")
            return v

        values = info.data if hasattr(info, "data") else {}
        # Build URL with async driver for runtime engine
        user = values.get("POSTGRES_USER")
        password = values.get("POSTGRES_PASSWORD")
        host = values.get("POSTGRES_SERVER")
        port = values.get("POSTGRES_PORT", 5432)
        db = values.get("POSTGRES_DB", "")
        return f"postgresql+psycopg_async://{user}:{password}@{host}:{port}/{db}"

    def get_alembic_url(self) -> str:
        """Get database URL for Alembic (uses sync driver)."""
        if self.DATABASE_URL:
            return self.DATABASE_URL.replace(
                "postgresql+psycopg_async://", "postgresql+psycopg://"
            )
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Logging settings
    LOG_LEVEL: str = "INFO"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Supabase settings
    SUPABASE_URL: str = "http://127.0.0.1:54321"
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    # OpenTelemetry settings
    OTEL_SERVICE_NAME: str = "sprintsense-backend"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"

    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None


settings = Settings()

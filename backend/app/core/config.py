"""Core configuration settings for SprintSense backend."""

from typing import Any, List, Optional

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=".env", env_file_encoding="utf-8"
    )

    PROJECT_NAME: str = "SprintSense"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Backwards-compatible alias used in tests
    @property
    def API_V1_PREFIX(self) -> str:  # pragma: no cover
        return self.API_V1_STR

    # Security settings
    SECRET_KEY: str = "a-secure-default-secret-that-should-be-overridden"
    JWT_SECRET_KEY: str = "a-secure-jwt-secret-key-that-should-be-overridden"
    JWT_ALGORITHM: str = "HS256"
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

    @model_validator(mode="before")
    @classmethod
    def assemble_db_connection(cls, data: Any) -> Any:
        """Assemble database URL from components."""
        if isinstance(data.get("DATABASE_URL"), str):
            # If the URL uses standard postgresql://, convert to async for runtime
            url = data["DATABASE_URL"]
            if url.startswith("postgresql://"):
                data["DATABASE_URL"] = url.replace(
                    "postgresql://", "postgresql+psycopg_async://"
                )
            return data

        # Build URL with async driver for runtime engine
        user = data.get("POSTGRES_USER")
        password = data.get("POSTGRES_PASSWORD")
        host = data.get("POSTGRES_SERVER")
        port = data.get("POSTGRES_PORT", 5432)
        db = data.get("POSTGRES_DB", "")
        data["DATABASE_URL"] = (
            f"postgresql+psycopg_async://{user}:{password}@{host}:{port}/{db}"
        )
        return data

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

    # Machine Learning settings
    DEPENDENCY_MODEL_PATH: Optional[str] = None

    # AWS settings
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    # LLM Security settings
    LLM_API_KEY_SECRET_ID: str = "test/llm/api-keys"
    LLM_PROVIDERS: List[str] = ["openai", "anthropic"]
    LLM_RATE_LIMIT_PER_MINUTE: int = 100
    
    # Security monitoring
    SECURITY_ALERT_CHANNELS: List[str] = ["slack", "email"]


settings = Settings()

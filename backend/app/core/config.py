"""Core configuration settings for SprintSense backend."""

from typing import Any, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    PROJECT_NAME: str = "SprintSense"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Assemble CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database settings (Supabase local development)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "postgres"
    POSTGRES_PORT: str = "54322"
    DATABASE_URL: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: Any) -> Any:
        """Assemble database URL from components."""
        if isinstance(v, str):
            return v
        values = info.data if hasattr(info, "data") else {}
        # Use async driver for runtime engine
        return PostgresDsn.build(
            scheme="postgresql+psycopg_async",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=int(values.get("POSTGRES_PORT", 5432)),
            path=values.get("POSTGRES_DB") or "",
        )

    # Logging settings
    LOG_LEVEL: str = "INFO"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # OpenTelemetry settings
    OTEL_SERVICE_NAME: str = "sprintsense-backend"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()

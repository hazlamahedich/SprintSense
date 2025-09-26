"""Logging configuration with structlog and OpenTelemetry integration."""

import logging
import os
import sys
from typing import Any, Dict

import structlog

from app.core.config import settings

# Lazy load OpenTelemetry imports
try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    HAS_OTEL = True
except ImportError:
    HAS_OTEL = False


def add_trace_info(
    logger: Any, name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Add trace and span IDs to log events."""
    if HAS_OTEL:
        span = trace.get_current_span()  # type: ignore[name-defined]
        if span != trace.INVALID_SPAN:  # type: ignore[name-defined]
            ctx = span.get_span_context()
            event_dict["trace_id"] = format(ctx.trace_id, "032x")
            event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict


def configure_logging() -> None:
    """Configure structured logging with OpenTelemetry integration."""

    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.StackInfoRenderer(),
        add_trace_info,
        structlog.processors.format_exc_info,
    ]

    if settings.ENVIRONMENT == "development":
        processors.extend([structlog.dev.ConsoleRenderer(colors=True)])
    else:
        processors.extend([structlog.processors.JSONRenderer()])

    structlog.configure(
        processors=processors,  # type: ignore[arg-type]
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )


def configure_tracing() -> None:
    """Configure OpenTelemetry tracing."""
    # Skip if OTEL is not available or during tests
    if (
        not HAS_OTEL
        or os.getenv("NODE_ENV") == "test"
        or os.getenv("PYTEST_DISABLE_OTEL") == "1"
        or "pytest" in sys.modules
    ):
        return

    # These variables are only available when HAS_OTEL is True
    resource = Resource.create(  # type: ignore[name-defined]
        {
            "service.name": settings.OTEL_SERVICE_NAME,
            "service.version": settings.VERSION,
        }
    )

    provider = TracerProvider(resource=resource)  # type: ignore[name-defined]

    # Configure OTLP exporter
    otlp_exporter = OTLPSpanExporter(  # type: ignore[name-defined]
        endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
        insecure=True,  # Use gRPC without TLS for local development
    )

    span_processor = BatchSpanProcessor(otlp_exporter)  # type: ignore[name-defined]
    provider.add_span_processor(span_processor)

    trace.set_tracer_provider(provider)  # type: ignore[name-defined]


def setup_instrumentation() -> None:
    """Set up all logging and tracing instrumentation."""
    configure_logging()

    # Only configure tracing if we have an endpoint
    if settings.OTEL_EXPORTER_OTLP_ENDPOINT:
        try:
            configure_tracing()
        except Exception as e:
            logger = structlog.get_logger(__name__)
            logger.warning(
                "Failed to configure OpenTelemetry tracing",
                error=str(e),
                endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
            )


def instrument_fastapi(app: Any) -> None:
    """Instrument FastAPI app with OpenTelemetry."""
    # Skip if OTEL is not available or during tests
    if (
        not HAS_OTEL
        or os.getenv("NODE_ENV") == "test"
        or os.getenv("PYTEST_DISABLE_OTEL") == "1"
        or "pytest" in sys.modules
    ):
        return

    try:
        FastAPIInstrumentor.instrument_app(app)  # type: ignore[name-defined]
    except Exception as e:
        logger = structlog.get_logger(__name__)
        logger.warning("Failed to instrument FastAPI with OpenTelemetry", error=str(e))

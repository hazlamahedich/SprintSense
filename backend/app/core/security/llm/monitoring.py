"""Security monitoring and event logging for LLM API."""

import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from prometheus_client import Counter, Gauge, Histogram
from redis import Redis

from app.core.config import settings
from app.core.logging import logger

class SecurityEventType(str, Enum):
    """Types of security events to monitor."""
    KEY_ROTATION = "key_rotation"
    PII_DETECTED = "pii_detected"
    QUOTA_EXCEEDED = "quota_exceeded"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    PERMISSION_DENIED = "permission_denied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

class SecurityEventSeverity(str, Enum):
    """Severity levels for security events."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

# Prometheus metrics
SECURITY_EVENTS = Counter(
    'llm_security_events_total',
    'Total security events by type',
    ['event_type', 'severity']
)

API_QUOTA_USAGE = Gauge(
    'llm_api_quota_usage_percent',
    'Current API quota usage percentage by team',
    ['team_id']
)

API_REQUEST_LATENCY = Histogram(
    'llm_api_request_latency_seconds',
    'API request latency in seconds',
    ['endpoint']
)

class SecurityEvent:
    """Security event data structure."""

    def __init__(
        self,
        event_type: SecurityEventType,
        severity: SecurityEventSeverity,
        details: Dict,
        user_id: Optional[int] = None,
        team_id: Optional[int] = None
    ):
        """Initialize a security event.

        Args:
            event_type: Type of security event
            severity: Event severity level
            details: Additional event details
            user_id: Associated user ID
            team_id: Associated team ID
        """
        self.event_type = event_type
        self.severity = severity
        self.details = details
        self.user_id = user_id
        self.team_id = team_id
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict:
        """Convert event to dictionary format.

        Returns:
            Dict representation of event
        """
        return {
            "type": self.event_type.value,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "team_id": self.team_id,
            "details": self.details
        }

class SecurityMonitor:
    """Monitors and logs security events for LLM API."""

    def __init__(self, redis_client: Redis):
        """Initialize the security monitor.

        Args:
            redis_client: Redis client for event storage
        """
        self.redis = redis_client
        self.event_key_prefix = "security_event:"
        self.alert_channels = settings.SECURITY_ALERT_CHANNELS

    async def log_event(self, event: SecurityEvent) -> None:
        """Log a security event.

        Args:
            event: The security event to log
        """
        try:
            # Store event in Redis
            event_id = f"{self.event_key_prefix}{int(event.timestamp.timestamp())}"
            self.redis.setex(
                event_id,
                timedelta(days=30),  # Store for 30 days
                json.dumps(event.to_dict())
            )

            # Update Prometheus metrics
            SECURITY_EVENTS.labels(
                event_type=event.event_type.value,
                severity=event.severity.value
            ).inc()

            # Log the event
            log_message = (
                f"Security Event: {event.event_type.value} "
                f"[{event.severity.value}]"
            )
            if event.severity in [
                SecurityEventSeverity.ERROR,
                SecurityEventSeverity.CRITICAL
            ]:
                logger.error(log_message, extra=event.to_dict())
                await self._send_alerts(event)
            else:
                logger.info(log_message, extra=event.to_dict())

        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")

    async def get_recent_events(
        self,
        event_type: Optional[SecurityEventType] = None,
        severity: Optional[SecurityEventSeverity] = None,
        hours: int = 24
    ) -> List[Dict]:
        """Get recent security events with optional filtering.

        Args:
            event_type: Filter by event type
            severity: Filter by severity level
            hours: How many hours of history to retrieve

        Returns:
            List of matching events
        """
        try:
            events = []
            since = datetime.utcnow() - timedelta(hours=hours)

            # Scan Redis for recent events
            for key in self.redis.scan_iter(f"{self.event_key_prefix}*"):
                event_data = json.loads(self.redis.get(key))
                event_time = datetime.fromisoformat(event_data['timestamp'])

                if event_time < since:
                    continue

                if event_type and event_data['type'] != event_type.value:
                    continue

                if severity and event_data['severity'] != severity.value:
                    continue

                events.append(event_data)

            return sorted(
                events,
                key=lambda x: x['timestamp'],
                reverse=True
            )

        except Exception as e:
            logger.error(f"Failed to retrieve security events: {str(e)}")
            return []

    async def get_security_metrics(self) -> Dict[str, Union[int, float, Dict]]:
        """Get current security metrics.

        Returns:
            Dict containing security metrics
        """
        try:
            now = datetime.utcnow()
            hour_ago = now - timedelta(hours=1)
            day_ago = now - timedelta(days=1)

            # Get events by timeframe
            hourly_events = await self.get_recent_events(hours=1)
            daily_events = await self.get_recent_events(hours=24)

            # Calculate metrics
            metrics = {
                "events_last_hour": len(hourly_events),
                "events_last_day": len(daily_events),
                "events_by_type": {},
                "events_by_severity": {},
                "active_alerts": 0
            }

            # Count events by type and severity
            for event in daily_events:
                metrics["events_by_type"][event["type"]] = \
                    metrics["events_by_type"].get(event["type"], 0) + 1

                metrics["events_by_severity"][event["severity"]] = \
                    metrics["events_by_severity"].get(event["severity"], 0) + 1

                if event["severity"] in [
                    SecurityEventSeverity.ERROR.value,
                    SecurityEventSeverity.CRITICAL.value
                ]:
                    metrics["active_alerts"] += 1

            return metrics

        except Exception as e:
            logger.error(f"Failed to generate security metrics: {str(e)}")
            return {
                "events_last_hour": 0,
                "events_last_day": 0,
                "events_by_type": {},
                "events_by_severity": {},
                "active_alerts": 0
            }

    async def _send_alerts(self, event: SecurityEvent) -> None:
        """Send alerts for critical security events.

        Args:
            event: The security event
        """
        if not self.alert_channels:
            return

        alert_message = (
            f"⚠️ Security Alert ⚠️\n"
            f"Type: {event.event_type.value}\n"
            f"Severity: {event.severity.value}\n"
            f"Time: {event.timestamp.isoformat()}\n"
            f"Details: {json.dumps(event.details, indent=2)}"
        )

        for channel in self.alert_channels:
            try:
                # In practice, integrate with notification services
                # (Slack, email, etc.)
                logger.warning(
                    f"Security Alert [{channel}]: {alert_message}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to send alert to {channel}: {str(e)}"
                )

class SecurityMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring security-related metrics."""

    def __init__(self, app: FastAPI, redis_client: Redis):
        super().__init__(app)
        self.monitor = SecurityMonitor(redis_client)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        """Process the request, monitoring security metrics."""
        # Start timing
        start_time = datetime.utcnow()

        # Add request tracking
        request_id = request.headers.get('X-Request-ID', 'unknown')
        logger.info(
            "API Request",
            extra={
                'request_id': request_id,
                'path': request.url.path,
                'method': request.method,
                'client_ip': request.client.host if request.client else None
            }
        )

        try:
            # Process request
            response = await call_next(request)

            # Record latency
            duration = (datetime.utcnow() - start_time).total_seconds()
            API_REQUEST_LATENCY.labels(
                endpoint=request.url.path
            ).observe(duration)

            return response

        except Exception as e:
            # Log security event for errors
            await self.monitor.log_event(
                SecurityEvent(
                    event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                    severity=SecurityEventSeverity.ERROR,
                    details={
                        'error': str(e),
                        'request_id': request_id,
                        'path': request.url.path
                    }
                )
            )
            raise

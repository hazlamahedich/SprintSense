"""Tests for security monitoring system."""

import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from prometheus_client import REGISTRY
from redis import Redis

from app.core.security.llm.monitoring import (
    SecurityEvent,
    SecurityEventSeverity,
    SecurityEventType,
    SecurityMonitor,
    SecurityMonitoringMiddleware
)

@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    redis = MagicMock(spec=Redis)
    redis.get.return_value = None
    redis.setex.return_value = True
    redis.scan_iter.return_value = []
    return redis

@pytest.fixture
def security_monitor(mock_redis):
    """Create a SecurityMonitor instance."""
    return SecurityMonitor(mock_redis)

@pytest.fixture
def test_app(mock_redis):
    """Create a test FastAPI application."""
    app = FastAPI()
    app.add_middleware(SecurityMonitoringMiddleware, redis_client=mock_redis)

    @app.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    @app.post("/test_error")
    async def error_endpoint():
        raise ValueError("Test error")

    return TestClient(app)

class TestSecurityEvent:
    """Test the SecurityEvent class."""

    def test_security_event_creation(self):
        """Test creating a security event."""
        event = SecurityEvent(
            event_type=SecurityEventType.PII_DETECTED,
            severity=SecurityEventSeverity.WARNING,
            details={"field": "email"},
            user_id=1,
            team_id=2
        )

        assert event.event_type == SecurityEventType.PII_DETECTED
        assert event.severity == SecurityEventSeverity.WARNING
        assert event.details == {"field": "email"}
        assert event.user_id == 1
        assert event.team_id == 2
        assert isinstance(event.timestamp, datetime)

    def test_security_event_to_dict(self):
        """Test converting security event to dictionary."""
        event = SecurityEvent(
            event_type=SecurityEventType.KEY_ROTATION,
            severity=SecurityEventSeverity.INFO,
            details={"provider": "openai"}
        )

        event_dict = event.to_dict()
        assert event_dict["type"] == "key_rotation"
        assert event_dict["severity"] == "info"
        assert event_dict["details"] == {"provider": "openai"}
        assert "timestamp" in event_dict

class TestSecurityMonitor:
    """Test the SecurityMonitor class."""

    @pytest.mark.asyncio
    async def test_log_event(self, security_monitor, mock_redis):
        """Test logging a security event."""
        event = SecurityEvent(
            event_type=SecurityEventType.QUOTA_EXCEEDED,
            severity=SecurityEventSeverity.WARNING,
            details={"team_id": 1}
        )

        await security_monitor.log_event(event)
        mock_redis.setex.assert_called_once()

        # Verify Prometheus metric
        event_counter = REGISTRY.get_sample_value(
            'llm_security_events_total',
            {'event_type': 'quota_exceeded', 'severity': 'warning'}
        )
        assert event_counter is not None

    @pytest.mark.asyncio
    async def test_get_recent_events(self, security_monitor, mock_redis):
        """Test retrieving recent events."""
        # Mock stored events
        event1 = {
            "type": "pii_detected",
            "severity": "warning",
            "timestamp": datetime.utcnow().isoformat(),
            "details": {}
        }
        event2 = {
            "type": "quota_exceeded",
            "severity": "error",
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "details": {}
        }

        mock_redis.scan_iter.return_value = ["event:1", "event:2"]
        mock_redis.get.side_effect = [
            json.dumps(event1),
            json.dumps(event2)
        ]

        # Get events from last hour
        events = await security_monitor.get_recent_events(hours=1)
        assert len(events) == 1
        assert events[0]["type"] == "pii_detected"

    @pytest.mark.asyncio
    async def test_get_recent_events_with_filters(
        self,
        security_monitor,
        mock_redis
    ):
        """Test retrieving events with type and severity filters."""
        event1 = {
            "type": "pii_detected",
            "severity": "warning",
            "timestamp": datetime.utcnow().isoformat(),
            "details": {}
        }
        event2 = {
            "type": "quota_exceeded",
            "severity": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "details": {}
        }

        mock_redis.scan_iter.return_value = ["event:1", "event:2"]
        mock_redis.get.side_effect = [
            json.dumps(event1),
            json.dumps(event2)
        ]

        events = await security_monitor.get_recent_events(
            event_type=SecurityEventType.PII_DETECTED,
            severity=SecurityEventSeverity.WARNING
        )
        assert len(events) == 1
        assert events[0]["type"] == "pii_detected"
        assert events[0]["severity"] == "warning"

    @pytest.mark.asyncio
    async def test_get_security_metrics(self, security_monitor, mock_redis):
        """Test generating security metrics."""
        event1 = {
            "type": "pii_detected",
            "severity": "warning",
            "timestamp": datetime.utcnow().isoformat(),
            "details": {}
        }
        event2 = {
            "type": "quota_exceeded",
            "severity": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "details": {}
        }

        mock_redis.scan_iter.return_value = ["security_event:1", "security_event:2"]
        redis_values = {
            "security_event:1": json.dumps(event1).encode('utf-8'),
            "security_event:2": json.dumps(event2).encode('utf-8')
        }
        mock_redis.get.side_effect = lambda k: redis_values.get(k)

        metrics = await security_monitor.get_security_metrics()
        assert metrics["events_last_day"] == 2
        assert metrics["events_by_type"]["pii_detected"] == 1
        assert metrics["events_by_type"]["quota_exceeded"] == 1
        assert metrics["events_by_severity"]["warning"] == 1
        assert metrics["events_by_severity"]["error"] == 1
        assert metrics["active_alerts"] == 1

    @pytest.mark.asyncio
    async def test_send_alerts(self, security_monitor):
        """Test sending security alerts."""
        event = SecurityEvent(
            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
            severity=SecurityEventSeverity.CRITICAL,
            details={"ip": "1.2.3.4"}
        )

        with patch('app.core.logging.logger.warning') as mock_logger:
            await security_monitor._send_alerts(event)
            assert mock_logger.called

class TestSecurityMonitoringMiddleware:
    """Test the security monitoring middleware."""

    def test_middleware_tracks_requests(self, test_app):
        """Test that middleware tracks normal requests."""
        response = test_app.get("/test")
        assert response.status_code == 200

        # Verify latency metric
        latency = REGISTRY.get_sample_value(
            'llm_api_request_latency_seconds_count',
            {'endpoint': '/test'}
        )
        assert latency is not None

    def test_middleware_handles_errors(self, test_app):
        """Test middleware error handling."""
        with pytest.raises(ValueError):
            test_app.post("/test_error")

        # Verify error event metric
        error_count = REGISTRY.get_sample_value(
            'llm_security_events_total',
            {
                'event_type': 'suspicious_activity',
                'severity': 'error'
            }
        )
        assert error_count is not None

    def test_middleware_adds_request_tracking(self, test_app):
        """Test request tracking headers."""
        request_id = "test-123"
        response = test_app.get(
            "/test",
            headers={"X-Request-ID": request_id}
        )
        assert response.status_code == 200
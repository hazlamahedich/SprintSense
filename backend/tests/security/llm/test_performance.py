"""Performance benchmarks for security components."""

import asyncio
import json
import os
import time
from typing import List
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.security.llm.key_rotation import LLMKeyRotationManager
from app.core.security.llm.monitoring import (SecurityEvent, SecurityEventSeverity,
                                          SecurityEventType)
from app.core.security.llm.pii_detection import PIIDetector
from app.core.security.llm.rbac import LLMRBACManager


# Module-scoped fixtures for performance tests
@pytest.fixture
def redis():
    """Mock Redis client."""
    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    mock_redis.setex.return_value = True
    mock_redis.scan_iter.return_value = []
    mock_redis.pipeline.return_value.execute.return_value = [True, True]
    mock_redis.pipeline.return_value.incr.return_value = mock_redis.pipeline.return_value
    mock_redis.pipeline.return_value.expire.return_value = mock_redis.pipeline.return_value
    return mock_redis


@pytest.fixture
def secrets_manager():
    """Mock AWS Secrets Manager."""
    mock_secrets = MagicMock()
    mock_secrets.get_secret_value.return_value = {
        'SecretString': json.dumps({"openai": "test-key"})
    }
    return mock_secrets


@pytest.fixture
def comprehend():
    """Mock AWS Comprehend."""
    mock_comprehend = MagicMock()
    mock_comprehend.detect_pii_entities.return_value = {
        'Entities': [
            {
                'Type': 'EMAIL',
                'BeginOffset': 0,
                'EndOffset': 10,
            }
        ]
    }
    return mock_comprehend


@pytest.fixture
def db():
    """Mock database session."""
    # Setup user mock
    user = MagicMock()
    user.role = 'user'

    # Setup team mock
    team = MagicMock()
    team.monthly_quota = 100000  # Large quota for tests

    # Build separate query chains
    user_filter = MagicMock()
    user_filter.first.return_value = user
    user_query = MagicMock()
    user_query.filter.return_value = user_filter

    team_filter = MagicMock()
    team_filter.first.return_value = team
    team_query = MagicMock()
    team_query.filter.return_value = team_filter

    def query_side_effect(model):
        try:
            name = getattr(model, '__name__', str(model))
        except Exception:
            name = str(model)
        if name == 'Team':
            return team_query
        return user_query

    mock_db = MagicMock()
    mock_db.query.side_effect = query_side_effect
    return mock_db


@pytest.fixture
def app(redis, secrets_manager, comprehend):
    """Create test FastAPI application."""
    app = FastAPI()
    return TestClient(app)


@pytest.mark.benchmark
class TestSecurityPerformance:
    """Performance tests for security components."""

    def generate_test_data(self, size: int) -> List[str]:
        """Generate test data of specified size."""
        return [
            f"User {i} (user{i}@example.com) with credit card 4111-1111-1111-{i:04d}"
            for i in range(size)
        ]

    @pytest.mark.asyncio
    async def test_pii_detection_performance(self, comprehend):
        """Test PII detection performance."""
        # Create a detector with mocked comprehend client
        detector = PIIDetector()
        detector.comprehend = comprehend
        test_data = self.generate_test_data(100)

        # Process test data in chunks to avoid timeouts
        chunk_size = 10
        chunks = [test_data[i:i + chunk_size] for i in range(0, len(test_data), chunk_size)]

        start_time = time.time()
        for chunk in chunks:
            tasks = [detector.detect_pii_async(text) for text in chunk]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                assert isinstance(result, list)  # Ensure we got valid results, not exceptions
                assert len(result) > 0

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / len(test_data)

        # Performance requirements
        assert avg_time < 0.05  # Average response time under 50ms
        assert total_time < 5.0  # Total processing under 5 seconds

    @pytest.mark.asyncio
    @patch.dict('os.environ', {
        'AWS_ACCESS_KEY_ID': 'test',
        'AWS_SECRET_ACCESS_KEY': 'test',
        'AWS_DEFAULT_REGION': 'us-east-1'
    })
    @patch('boto3.client')
    async def test_key_rotation_performance(self, mock_boto3, redis, secrets_manager):
        """Test key rotation performance."""
        mock_boto3.return_value = secrets_manager
        manager = LLMKeyRotationManager(redis)
        manager.secrets_manager = secrets_manager

        start_time = time.time()
        # Test cache hit performance
        for _ in range(1000):
            key = manager.get_current_key("openai")
            assert key is not None
        cache_hit_time = time.time() - start_time

        # Clear cache and test cache miss performance
        redis.get.return_value = None
        start_time = time.time()
        for _ in range(10):
            key = manager.get_current_key("openai")
            assert key is not None
        cache_miss_time = time.time() - start_time

        # Performance requirements
        assert cache_hit_time < 1.0  # 1000 cache hits under 1 second
        assert cache_miss_time / 10 < 0.1  # Cache misses under 100ms each

    @pytest.mark.asyncio
    async def test_rbac_quota_performance(self, redis, db):
        """Test RBAC and quota tracking performance."""
        manager = LLMRBACManager(db, redis)
        tasks = []

        start_time = time.time()
        # Simulate concurrent quota checks
        for i in range(100):
            tasks.append(
                manager.check_quota(user_id=1, team_id=1, tokens=10)
            )

        await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time
        avg_time = total_time / len(tasks)

        # Performance requirements
        assert avg_time < 0.01  # Average quota check under 10ms
        assert total_time < 1.0  # 100 concurrent checks under 1 second

    @pytest.mark.asyncio
    async def test_monitoring_performance(self, redis):
        """Test security monitoring performance."""
        from app.core.security.llm.monitoring import SecurityMonitor

        monitor = SecurityMonitor(redis)
        events = [
            SecurityEvent(
                event_type=SecurityEventType.PII_DETECTED,
                severity=SecurityEventSeverity.WARNING,
                details={"field": f"test{i}"},
                user_id=1,
                team_id=1
            )
            for i in range(100)
        ]

        start_time = time.time()
        # Test event logging performance
        for event in events:
            await monitor.log_event(event)
        logging_time = time.time() - start_time

        start_time = time.time()
        # Test event retrieval performance
        events = await monitor.get_recent_events(hours=24)
        retrieval_time = time.time() - start_time

        # Performance requirements
        assert logging_time < 2.0  # 100 events logged under 2 seconds
        assert retrieval_time < 0.5  # Event retrieval under 500ms

    @pytest.mark.asyncio
    @patch.dict('os.environ', {
        'AWS_ACCESS_KEY_ID': 'test',
        'AWS_SECRET_ACCESS_KEY': 'test',
        'AWS_DEFAULT_REGION': 'us-east-1'
    })
    async def test_end_to_end_performance(self, app, redis, db, comprehend, secrets_manager):
        """Test end-to-end security component performance."""
        # Simulate complete request flow
        start_time = time.time()

        # 1. Check permissions
        rbac = LLMRBACManager(db, redis)
        rbac.check_permission(1, "can_create")

        # 2. Check quota
        await rbac.check_quota(1, 1, 100)

        # 3. PII detection
        detector = PIIDetector()
        detector.comprehend = comprehend  # Use mocked client
        text = "Send email to user@example.com"
        await detector.detect_pii_async(text)

        # 4. Get API key
        key_manager = LLMKeyRotationManager(redis)
        key_manager.secrets_manager = secrets_manager
        key = key_manager.get_current_key("openai")
        assert key == "test-key"  # Verify we got the test key

        end_time = time.time()
        total_time = end_time - start_time

        # Performance requirement: Complete flow under 250ms
        assert total_time < 0.25
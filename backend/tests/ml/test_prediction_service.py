"""Tests for ML prediction service with lightweight models."""

import json
from unittest.mock import Mock, patch

import pytest

from app.core.circuit_breaker import CircuitBreakerError
from app.domains.ml.services.prediction_service import PredictionService

# Test data
TEST_TITLE = "Implement OAuth2 authentication"
TEST_DESCRIPTION = "Add OAuth2 authentication flow with JWT tokens"
TEST_TEAM_CONTEXT = {
    "team_velocity": 20.0,
    "sprint_capacity": 80.0,
    "avg_completion_time": 3.5,
}


@pytest.fixture
def prediction_service():
    """Create prediction service fixture."""
    return PredictionService()


@pytest.mark.asyncio
async def test_analyze_work_item(prediction_service):
    """Test work item analysis."""
    # Run analysis
    patterns, pattern_conf, priority, explanation = (
        await prediction_service.analyze_work_item(
            TEST_TITLE, TEST_DESCRIPTION, TEST_TEAM_CONTEXT
        )
    )

    # Check pattern results
    assert isinstance(patterns, list)
    assert "auth" in patterns  # Should detect auth pattern
    assert "security" in patterns  # Should detect security pattern
    assert 0 <= pattern_conf <= 1.0
    assert pattern_conf > 0.7  # High confidence for auth patterns

    # Check priority results
    assert isinstance(priority, float)
    assert 0.5 < priority <= 1.0  # Higher priority for auth/security

    # Check explanations
    assert "patterns" in explanation
    assert "priority" in explanation
    assert explanation["patterns"]["auth"] > 0.5  # Strong auth evidence
    assert "team_velocity" in explanation["priority"]


@pytest.mark.asyncio
async def test_error_handling(prediction_service):
    """Test error handling in analysis."""
    # Test with empty inputs
    with pytest.raises(ValueError):
        await prediction_service.analyze_work_item("", "", {})

    # Test with invalid team context
    with pytest.raises(ValueError):
        await prediction_service.analyze_work_item(
            TEST_TITLE, TEST_DESCRIPTION, {"invalid": "context"}
        )


@pytest.mark.asyncio
async def test_feature_extraction(prediction_service):
    """Test feature extraction."""
    features = prediction_service._extract_features(
        TEST_TITLE, TEST_DESCRIPTION, ["auth", "security"]
    )

    # Check basic features
    assert isinstance(features, dict)
    assert features["title_length"] == len(TEST_TITLE)
    assert features["description_length"] == len(TEST_DESCRIPTION)

    # Check pattern features
    assert features["has_pattern_auth"] == 1.0
    assert features["has_pattern_security"] == 1.0
    assert features["has_pattern_frontend"] == 0.0


@pytest.mark.asyncio
async def test_metrics_logging(prediction_service):
    """Test metrics logging."""
    with patch("app.domains.ml.services.prediction_service.logger.info") as mock_log:
        # Run analysis to trigger metrics
        await prediction_service.analyze_work_item(
            TEST_TITLE, TEST_DESCRIPTION, TEST_TEAM_CONTEXT
        )

        # Verify metrics were logged
        assert mock_log.call_count >= 1
        msg = mock_log.call_args_list[0][0][0]
        assert msg.startswith("prediction_service_metrics: ")
        metrics_str = msg.split(": ", 1)[1]
        metrics = json.loads(metrics_str)
        assert metrics["success"] is True


@pytest.mark.asyncio
async def test_circuit_breaker(prediction_service):
    """Test circuit breaker functionality."""
    # Mock pattern model to raise exceptions
    prediction_service.pattern_model.predict = Mock(
        side_effect=ValueError("Model error")
    )

    # Make multiple failing calls
    for _ in range(5):
        with pytest.raises(ValueError):
            await prediction_service.analyze_work_item(
                TEST_TITLE, TEST_DESCRIPTION, TEST_TEAM_CONTEXT
            )

    # Next call should be blocked by circuit breaker
    with pytest.raises(CircuitBreakerError):
        await prediction_service.analyze_work_item(
            TEST_TITLE, TEST_DESCRIPTION, TEST_TEAM_CONTEXT
        )


@pytest.mark.asyncio
async def test_different_work_items(prediction_service):
    """Test analysis of different work item types."""
    # Frontend-focused work item
    patterns1, _, priority1, _ = await prediction_service.analyze_work_item(
        "Update button component styles",
        "Implement new UI design for buttons with CSS improvements",
        TEST_TEAM_CONTEXT,
    )
    assert "frontend" in patterns1
    assert priority1 < 0.7  # Lower priority for UI tasks

    # Security-focused work item
    patterns2, _, priority2, _ = await prediction_service.analyze_work_item(
        "Fix XSS vulnerability",
        "Patch critical security issue in input validation",
        TEST_TEAM_CONTEXT,
    )
    assert "security" in patterns2
    assert priority2 > 0.7  # Higher priority for security tasks

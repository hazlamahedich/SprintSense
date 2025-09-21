"""Tests for ML models with lightweight implementations."""

import pytest

from app.domains.ml.models.pattern_recognition import PatternRecognitionModel
from app.domains.ml.models.priority_prediction import PriorityPredictionModel

# Test data
TEST_TEXT = "Implement user authentication with OAuth2 and JWT tokens"
TEST_FEATURES = {
    "title_length": 50,
    "description_length": 200,
    "title_word_count": 10,
    "description_word_count": 40,
    "has_pattern_auth": 1.0,
    "has_pattern_security": 1.0,
    "has_pattern_frontend": 0.0,
}
TEST_TEAM_CONTEXT = {
    "team_velocity": 20.0,
    "sprint_capacity": 80.0,
    "avg_completion_time": 3.5,
}


@pytest.fixture
def pattern_model():
    """Create pattern recognition model fixture."""
    return PatternRecognitionModel()


@pytest.fixture
def priority_model():
    """Create priority prediction model fixture."""
    return PriorityPredictionModel()


def test_pattern_recognition(pattern_model):
    """Test pattern recognition model predictions."""
    # Get predictions
    patterns, confidence = pattern_model.predict(TEST_TEXT)

    # Check predictions
    assert isinstance(patterns, list)
    assert all(isinstance(p, str) for p in patterns)
    assert 0 <= confidence <= 1.0
    assert "auth" in patterns  # Should detect auth pattern
    assert "security" in patterns  # Should detect security pattern

    # Check explanations
    explanation = pattern_model.get_explanation(TEST_TEXT, patterns)
    assert isinstance(explanation, dict)
    assert all(isinstance(k, str) for k in explanation.keys())
    assert all(isinstance(v, float) for v in explanation.values())
    assert explanation["auth"] > 0.5  # High evidence for auth pattern


def test_priority_prediction(priority_model):
    """Test priority prediction model."""
    # Get predictions
    priority, confidence = priority_model.predict(TEST_FEATURES, TEST_TEAM_CONTEXT)

    # Check predictions
    assert isinstance(priority, float)
    assert 0 <= priority <= 1.0
    assert 0 <= confidence <= 1.0
    assert priority > 0.5  # High priority due to security patterns

    # Check explanations
    explanation = priority_model.get_explanation(TEST_FEATURES, TEST_TEAM_CONTEXT)
    assert isinstance(explanation, dict)
    assert all(isinstance(k, str) for k in explanation.keys())
    assert all(isinstance(v, float) for v in explanation.values())
    assert explanation["has_pattern_auth"] > 0  # Auth pattern influence
    assert explanation["has_pattern_security"] > 0  # Security pattern influence


def test_model_error_handling(pattern_model, priority_model):
    """Test model error handling."""
    # Test with invalid inputs
    with pytest.raises(ValueError):
        pattern_model.predict("")

    with pytest.raises(ValueError):
        priority_model.predict({}, {})

    # Test with malformed inputs
    with pytest.raises(ValueError):
        pattern_model.predict(123)  # type: ignore

    with pytest.raises(ValueError):
        priority_model.predict({"invalid": "feature"}, {"invalid": "context"})


def test_no_patterns_found(pattern_model):
    """Test behavior when no patterns are found."""
    text = "Simple text without any technical patterns"
    patterns, confidence = pattern_model.predict(text)

    assert isinstance(patterns, list)
    assert len(patterns) == 0  # No patterns detected
    assert 0 <= confidence <= 0.3  # Low confidence


def test_multiple_patterns(pattern_model):
    """Test detection of multiple patterns."""
    text = "Implement OAuth2 authentication UI components with performance optimization"
    patterns, confidence = pattern_model.predict(text)

    # Should detect auth, frontend, and performance patterns
    assert "auth" in patterns
    assert "frontend" in patterns
    assert "performance" in patterns
    assert confidence > 0.7  # High confidence with multiple matches

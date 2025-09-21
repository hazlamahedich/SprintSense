"""Service layer for ML model predictions using lightweight models."""

import json
import logging
from typing import Dict, List, Tuple

from app.core.circuit_breaker import CircuitBreaker, CircuitBreakerError
from app.domains.ml.models.pattern_recognition import (
    DEFAULT_PATTERNS,
    PatternRecognitionModel,
)
from app.domains.ml.models.priority_prediction import PriorityPredictionModel

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for managing work item analysis using lightweight models."""

    def __init__(self):
        """Initialize prediction service with lightweight models."""
        self.pattern_model = PatternRecognitionModel()
        self.priority_model = PriorityPredictionModel()
        # Persist circuit breaker across calls to accumulate failures
        self._pattern_breaker = CircuitBreaker(
            failure_threshold=5, recovery_timeout=30.0, name="pattern_recognition"
        )

    async def analyze_work_item(
        self, title: str, description: str, team_context: Dict[str, float]
    ) -> Tuple[List[str], float, float, Dict[str, Dict[str, float]]]:
        """Analyze work item text using heuristic-based models.

        Args:
            title: Work item title
            description: Work item description
            team_context: Team-specific context features

        Returns:
            Tuple of:
            - List[str]: Detected patterns
            - float: Pattern confidence score
            - float: Priority score
            - Dict: Explanations for patterns and priority

        Raises:
            ValueError: For invalid or empty inputs
            CircuitBreakerError: When too many errors occur
        """
        # Input validation
        if not isinstance(title, str) or not isinstance(description, str):
            raise ValueError("title and description must be strings")
        if not isinstance(team_context, dict):
            raise ValueError("team_context must be a dictionary")
        if not all(isinstance(v, (int, float)) for v in team_context.values()):
            raise ValueError("team_context values must be numeric")
        if not set(team_context.keys()).issuperset(
            {"team_velocity", "sprint_capacity", "avg_completion_time"}
        ):
            raise ValueError("team_context missing required fields")

        # Clean inputs
        title = title.strip()
        description = description.strip()
        if not title or not description:
            raise ValueError("title and description cannot be empty")

        try:
            # Initialize results in case of circuit breaker
            text = f"{title}\n\n{description}"
            patterns = []
            pattern_confidence = 0.0
            pattern_explanation = {}

            # Pattern recognition with circuit breaker (persistent across service lifetime)
            async with self._pattern_breaker:
                # Let any exceptions propagate for the circuit breaker
                patterns, pattern_confidence = self.pattern_model.predict(text)
                pattern_explanation = self.pattern_model.get_explanation(text, patterns)

            # Extract features and get priority prediction
            features = self._extract_features(title, description, patterns)
            priority_score, priority_confidence = self.priority_model.predict(
                features, team_context
            )
            priority_explanation = self.priority_model.get_explanation(
                features, team_context
            )

            # Adjust priority score for security patterns
            if "security" in patterns:
                priority_score = min(
                    1.0, priority_score * 1.5
                )  # Boost security priority

            # Combine explanations
            explanation = {
                "patterns": pattern_explanation,
                "priority": priority_explanation,
            }

            # Log success metrics
            metrics_str = json.dumps(
                {
                    "success": True,
                    "num_patterns": len(patterns),
                    "pattern_confidence": pattern_confidence,
                    "priority_score": priority_score,
                    "priority_confidence": priority_confidence,
                    "patterns": patterns,
                }
            )
            logger.info(f"prediction_service_metrics: {metrics_str}")

            return patterns, pattern_confidence, priority_score, explanation

        except (ValueError, CircuitBreakerError) as e:
            # Log error metrics
            metrics_str = json.dumps(
                {
                    "success": False,
                    "error": True,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                }
            )
            logger.error("Error in work item analysis", exc_info=True)
            logger.info(f"prediction_service_metrics: {metrics_str}")
            raise

    def _extract_features(
        self, title: str, description: str, patterns: List[str]
    ) -> Dict[str, float]:
        """Extract features from work item text.

        Args:
            title: Work item title
            description: Work item description
            patterns: Detected patterns

        Returns:
            Dictionary of normalized features
        """
        # Basic text features
        features = {
            "title_length": float(len(title)),
            "description_length": float(len(description)),
            "title_word_count": float(len(title.split())),
            "description_word_count": float(len(description.split())),
        }

        # Pattern presence features
        for pattern in DEFAULT_PATTERNS.keys():
            features[f"has_pattern_{pattern}"] = float(pattern in patterns)

        return features

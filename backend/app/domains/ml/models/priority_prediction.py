"""Priority Prediction Model for Work Items (lightweight)."""

import logging
from typing import Dict, Tuple

# Using standard logging for lightweight metrics

logger = logging.getLogger(__name__)


class PriorityPredictionModel:
    """Lightweight rule-based priority prediction.
    Avoids heavy dependencies and training during tests/local runs.
    """

    def __init__(self):
        pass

    def predict(
        self,
        features: Dict[str, float],
        team_context: Dict[str, float],
    ) -> Tuple[float, float]:
        """Predict priority score with a simple heuristic.
        Raises ValueError for invalid inputs.
        """
        if (
            not isinstance(features, dict)
            or not isinstance(team_context, dict)
            or not features
            or not team_context
        ):
            raise ValueError("features and team_context must be non-empty dicts")

        # Validate required feature names
        required_features = {
            "title_length",
            "description_length",
            "title_word_count",
            "description_word_count",
        }
        if not all(k in features for k in required_features):
            raise ValueError("missing required features")

        # Validate team context fields
        required_context = {"team_velocity", "sprint_capacity", "avg_completion_time"}
        if not all(k in team_context for k in required_context):
            raise ValueError("missing required team context fields")

        # Base score
        score = 0.5

        # Pattern influence
        for k, v in features.items():
            if k.startswith("has_pattern_") and v:
                score += 0.08  # each relevant pattern slightly increases

        # Team context influence
        team_velocity = float(team_context.get("team_velocity", 0.0))
        sprint_capacity = float(team_context.get("sprint_capacity", 0.0))
        avg_completion_time = float(team_context.get("avg_completion_time", 0.0))

        # Normalize influences
        score += min(team_velocity / 200.0, 0.1)
        score += min(sprint_capacity / 1000.0, 0.05)
        score -= min(avg_completion_time / 50.0, 0.1)

        # Clamp to [0, 1]
        priority_score = max(0.0, min(1.0, score))

        # Confidence heuristic: more signals -> higher confidence
        signals = sum(
            1 for k, v in features.items() if k.startswith("has_pattern_") and v
        )
        confidence = max(0.5, min(1.0, 0.5 + signals * 0.1))

        self._log_prediction_metrics(priority_score, confidence)
        return float(priority_score), float(confidence)

    def _log_prediction_metrics(self, priority_score: float, confidence: float) -> None:
        logger.info(
            "priority_prediction_metrics",
            extra={
                "priority_score": priority_score,
                "confidence": confidence,
            },
        )

    def get_explanation(
        self,
        features: Dict[str, float],
        team_context: Dict[str, float],
    ) -> Dict[str, float]:
        """Return simple feature attributions from heuristic weights."""
        if (
            not isinstance(features, dict)
            or not isinstance(team_context, dict)
            or not features
            or not team_context
        ):
            raise ValueError("features and team_context must be non-empty dicts")

        explanation: Dict[str, float] = {}
        for k, v in features.items():
            if k.startswith("has_pattern_"):
                explanation[k] = 0.08 if v else 0.0
        explanation["team_velocity"] = min(
            float(team_context.get("team_velocity", 0.0)) / 200.0, 0.1
        )
        explanation["sprint_capacity"] = min(
            float(team_context.get("sprint_capacity", 0.0)) / 1000.0, 0.05
        )
        explanation["avg_completion_time"] = -min(
            float(team_context.get("avg_completion_time", 0.0)) / 50.0, 0.1
        )
        return explanation

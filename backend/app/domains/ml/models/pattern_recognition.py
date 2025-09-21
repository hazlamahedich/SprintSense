"""Pattern Recognition Model for Work Item Analysis (lightweight)."""

import logging
import re
from typing import Dict, List, Optional, Tuple

# Using standard logging for lightweight metrics

logger = logging.getLogger(__name__)

DEFAULT_PATTERNS = {
    "auth": [r"(?i)auth", r"(?i)oauth", r"(?i)login", r"(?i)token", r"(?i)credentials"],
    "security": [
        r"(?i)security",
        r"(?i)xss",
        r"(?i)csrf",
        r"(?i)encrypt",
        r"(?i)secret",
        r"(?i)vulnerability",
        r"(?i)jwt",
        r"(?i)validation",
        r"(?i)auth",
        r"(?i)token",
    ],
    "frontend": [
        r"(?i)ui",
        r"(?i)button",
        r"(?i)react",
        r"(?i)component",
        r"(?i)css",
        r"(?i)style",
    ],
    "performance": [
        r"(?i)latency",
        r"(?i)throughput",
        r"(?i)optimi",
        r"(?i)cache",
        r"(?i)speed",
        r"(?i)performance",
    ],
}

DEFAULT_THRESHOLD = 0.3  # Lower threshold for better pattern detection


class PatternRecognitionModel:
    """Rule-based lightweight pattern recognition model.
    This avoids heavyweight model downloads during tests and local dev.
    """

    def __init__(
        self,
        pattern_labels: Optional[List[str]] = None,
        threshold: float = DEFAULT_THRESHOLD,
    ):
        """Initialize pattern recognition model.

        Args:
            pattern_labels: Optional list of pattern labels to use. Defaults to DEFAULT_PATTERNS keys.
            threshold: Pattern match threshold. Defaults to 0.5.
        """
        self.pattern_labels = pattern_labels or list(DEFAULT_PATTERNS.keys())
        self.threshold = threshold

    def predict(self, text: str) -> Tuple[List[str], float]:
        """Predict patterns in text with a simple keyword heuristic.
        Raises ValueError for empty input.
        """
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string")
        if not isinstance(text, str):
            raise ValueError("input must be a string")

        scores: Dict[str, float] = {}
        total_hits = 0
        for label in self.pattern_labels:
            keywords = DEFAULT_PATTERNS.get(label, [])
            hits = sum(bool(re.search(k, text)) for k in keywords)
            total_hits += hits
            # Score is weighted by number of hits and normalized
            score = 2 * hits / max(1, len(keywords))
            scores[label] = score

        # Select patterns above threshold
        predictions = [
            label for label, score in scores.items() if score >= self.threshold
        ]
        # Confidence is higher when more unique patterns are detected
        confidence = float(
            len(predictions) * sum(scores.values()) / max(1, len(self.pattern_labels))
        )

        # Log metrics
        metrics_data = {
            "num_patterns": len(predictions),
            "confidence": confidence,
            "metrics": {k: float(v) for k, v in scores.items()},
        }
        logger.info("pattern_recognition_metrics", extra=metrics_data)
        return predictions, confidence

    def _log_prediction_metrics(self, num_patterns: int, confidence: float) -> None:
        metrics_data = {
            "num_patterns": num_patterns,
            "confidence": confidence,
        }
        logger.info("pattern_recognition_metrics", extra={"metrics": metrics_data})

    def get_explanation(self, text: str, patterns: List[str]) -> Dict[str, float]:
        """Return a simple explanation score per pattern based on keyword hits."""
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string")

        text_lower = text.lower()
        explanation: Dict[str, float] = {}
        for pattern in patterns:
            keywords = DEFAULT_PATTERNS.get(pattern, [])
            hits = sum(bool(re.search(k, text_lower)) for k in keywords)
            explanation[pattern] = hits / max(1, len(keywords))
        return explanation

"""Recommendation metrics logging and monitoring."""

import logging
from datetime import datetime
from typing import Dict, Optional, Union
from prometheus_client import Counter, Histogram, Gauge

# Configure logger
logger = logging.getLogger(__name__)

# Prometheus metrics
RECOMMENDATION_COUNTER = Counter(
    'sprintsense_recommendations_total',
    'Total number of recommendations generated',
    ['team_id', 'status']
)

RECOMMENDATION_ACCEPTANCE_GAUGE = Gauge(
    'sprintsense_recommendation_acceptance_rate',
    'Current acceptance rate of recommendations',
    ['team_id']
)

FEEDBACK_REASON_COUNTER = Counter(
    'sprintsense_recommendation_feedback_total',
    'Total feedback counts by reason',
    ['team_id', 'reason']
)

CONFIDENCE_HISTOGRAM = Histogram(
    'sprintsense_recommendation_confidence',
    'Distribution of recommendation confidence scores',
    ['team_id'],
    buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
)

RESPONSE_TIME_HISTOGRAM = Histogram(
    'sprintsense_recommendation_response_time_seconds',
    'Response time for recommendation generation',
    ['team_id', 'endpoint']
)


class MetricsLogger:
    """Logger for recommendation metrics with Prometheus integration."""

    def log_recommendation_generated(
        self,
        team_id: str,
        recommendation_id: str,
        confidence_score: float,
        processing_time: float
    ) -> None:
        """Log a generated recommendation with metrics."""
        RECOMMENDATION_COUNTER.labels(team_id=team_id, status='generated').inc()
        CONFIDENCE_HISTOGRAM.labels(team_id=team_id).observe(confidence_score)
        RESPONSE_TIME_HISTOGRAM.labels(
            team_id=team_id,
            endpoint='generate'
        ).observe(processing_time)

        logger.info(
            'Recommendation generated',
            extra={
                'team_id': team_id,
                'recommendation_id': recommendation_id,
                'confidence_score': confidence_score,
                'processing_time': processing_time,
                'timestamp': datetime.utcnow().isoformat()
            }
        )

    def log_recommendation_accepted(
        self,
        team_id: str,
        recommendation_id: str,
        acceptance_rate: float
    ) -> None:
        """Log an accepted recommendation."""
        RECOMMENDATION_COUNTER.labels(team_id=team_id, status='accepted').inc()
        RECOMMENDATION_ACCEPTANCE_GAUGE.labels(team_id=team_id).set(acceptance_rate)

        logger.info(
            'Recommendation accepted',
            extra={
                'team_id': team_id,
                'recommendation_id': recommendation_id,
                'new_acceptance_rate': acceptance_rate,
                'timestamp': datetime.utcnow().isoformat()
            }
        )

    def log_recommendation_feedback(
        self,
        team_id: str,
        recommendation_id: str,
        feedback_type: str,
        reason: Optional[str] = None
    ) -> None:
        """Log feedback received for a recommendation."""
        RECOMMENDATION_COUNTER.labels(team_id=team_id, status=feedback_type).inc()
        if reason:
            FEEDBACK_REASON_COUNTER.labels(team_id=team_id, reason=reason).inc()

        logger.info(
            'Recommendation feedback received',
            extra={
                'team_id': team_id,
                'recommendation_id': recommendation_id,
                'feedback_type': feedback_type,
                'reason': reason,
                'timestamp': datetime.utcnow().isoformat()
            }
        )

    def log_metrics_request(
        self,
        team_id: str,
        processing_time: float,
        metrics: Dict[str, Union[float, int, str, Dict]]
    ) -> None:
        """Log metrics request processing."""
        RESPONSE_TIME_HISTOGRAM.labels(
            team_id=team_id,
            endpoint='metrics'
        ).observe(processing_time)

        logger.info(
            'Quality metrics generated',
            extra={
                'team_id': team_id,
                'processing_time': processing_time,
                'metrics': metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
        )


# Global instance
metrics_logger = MetricsLogger()

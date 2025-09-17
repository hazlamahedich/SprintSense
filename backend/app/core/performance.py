"""
Performance monitoring and validation system for SprintSense application.

This module addresses QA Concern 3: Performance Validation Strategy
by providing measurement tools, monitoring, and validation approaches.
"""

import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import wraps
from typing import Any, AsyncGenerator, Callable, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""

    operation: str
    duration_ms: float
    success: bool
    error_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PerformanceMonitor:
    """Performance monitoring and validation system."""

    def __init__(self):
        self.metrics: list[PerformanceMetrics] = []
        self.thresholds = {
            "work_item_creation": 1000,  # 1 second threshold
            "priority_calculation": 500,  # 500ms for priority calc
            "database_query": 300,  # 300ms for individual queries
            "form_validation": 100,  # 100ms for validation
        }

    def record_metric(self, metric: PerformanceMetrics) -> None:
        """Record a performance metric."""
        self.metrics.append(metric)

        # Log performance issues
        threshold = self.thresholds.get(metric.operation, 1000)
        if metric.duration_ms > threshold:
            logger.warning(
                f"Performance threshold exceeded: {metric.operation} "
                f"took {metric.duration_ms:.2f}ms (threshold: {threshold}ms)"
            )

    def get_metrics_summary(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics summary."""
        filtered_metrics = self.metrics
        if operation:
            filtered_metrics = [m for m in self.metrics if m.operation == operation]

        if not filtered_metrics:
            return {"operation": operation, "count": 0}

        durations = [m.duration_ms for m in filtered_metrics]
        success_count = sum(1 for m in filtered_metrics if m.success)

        return {
            "operation": operation or "all",
            "count": len(filtered_metrics),
            "avg_duration_ms": sum(durations) / len(durations),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "success_rate": success_count / len(filtered_metrics) * 100,
            "threshold_violations": sum(
                1
                for m in filtered_metrics
                if m.duration_ms > self.thresholds.get(m.operation, 1000)
            ),
        }

    def clear_metrics(self) -> None:
        """Clear all recorded metrics."""
        self.metrics.clear()


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


@asynccontextmanager
async def measure_performance(
    operation: str, metadata: Optional[Dict[str, Any]] = None
) -> AsyncGenerator[PerformanceMetrics, None]:
    """
    Context manager for measuring operation performance.

    Usage:
        async with measure_performance("work_item_creation") as metric:
            # Perform operation
            result = await create_work_item(...)
            # metric.success will be True if no exception is raised
    """
    start_time = time.perf_counter()
    metric = PerformanceMetrics(
        operation=operation, duration_ms=0.0, success=False, metadata=metadata or {}
    )

    try:
        yield metric
        metric.success = True
    except Exception as e:
        metric.success = False
        metric.error_type = type(e).__name__
        raise
    finally:
        end_time = time.perf_counter()
        metric.duration_ms = (end_time - start_time) * 1000
        performance_monitor.record_metric(metric)


def monitor_performance(operation: str, metadata: Optional[Dict[str, Any]] = None):
    """Decorator for monitoring async function performance."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with measure_performance(operation, metadata):
                return await func(*args, **kwargs)

        return wrapper

    return decorator


class PerformanceValidator:
    """Validates that operations meet performance requirements."""

    @staticmethod
    def validate_work_item_creation_performance(duration_ms: float) -> bool:
        """Validate work item creation meets <1s requirement."""
        return duration_ms < 1000

    @staticmethod
    def validate_priority_calculation_performance(duration_ms: float) -> bool:
        """Validate priority calculation meets <500ms requirement."""
        return duration_ms < 500

    @staticmethod
    def validate_form_submission_performance(duration_ms: float) -> bool:
        """Validate form submission meets <1s total requirement."""
        return duration_ms < 1000

    @staticmethod
    def generate_performance_report() -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        report = {
            "timestamp": time.time(),
            "summary": performance_monitor.get_metrics_summary(),
            "operations": {},
        }

        # Get operation-specific summaries
        operations = set(m.operation for m in performance_monitor.metrics)
        for op in operations:
            report["operations"][op] = performance_monitor.get_metrics_summary(op)

        return report


# Performance testing utilities
async def benchmark_work_item_creation(
    service, team_id: str, author_id: str, num_iterations: int = 10
) -> Dict[str, Any]:
    """Benchmark work item creation performance."""

    durations = []
    errors = []

    for i in range(num_iterations):
        try:
            async with measure_performance("benchmark_work_item_creation") as metric:
                # Create test work item
                from app.domains.models.work_item import WorkItemType
                from app.domains.schemas.work_item import WorkItemCreateRequest

                request = WorkItemCreateRequest(
                    team_id=team_id,
                    title=f"Benchmark Work Item {i}",
                    description="Performance test work item",
                    type=WorkItemType.TASK,
                )

                await service.create_work_item(request, author_id)
                durations.append(metric.duration_ms)

        except Exception as e:
            errors.append(str(e))

    return {
        "iterations": num_iterations,
        "successful": len(durations),
        "failed": len(errors),
        "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
        "min_duration_ms": min(durations) if durations else 0,
        "max_duration_ms": max(durations) if durations else 0,
        "errors": errors,
        "performance_threshold_met": all(d < 1000 for d in durations),
    }


async def run_performance_validation() -> Dict[str, Any]:
    """Run complete performance validation suite."""

    validation_results = {
        "timestamp": time.time(),
        "validations": {},
        "overall_passed": True,
    }

    # Check recent metrics
    summary = performance_monitor.get_metrics_summary("work_item_creation")

    if summary["count"] > 0:
        # Validate average response time
        avg_meets_threshold = summary["avg_duration_ms"] < 1000
        max_meets_threshold = summary["max_duration_ms"] < 2000  # Allow some outliers
        success_rate_acceptable = summary["success_rate"] > 95

        validation_results["validations"]["work_item_creation"] = {
            "avg_response_time_ok": avg_meets_threshold,
            "max_response_time_ok": max_meets_threshold,
            "success_rate_ok": success_rate_acceptable,
            "avg_duration_ms": summary["avg_duration_ms"],
            "max_duration_ms": summary["max_duration_ms"],
            "success_rate": summary["success_rate"],
        }

        if not all([avg_meets_threshold, max_meets_threshold, success_rate_acceptable]):
            validation_results["overall_passed"] = False

    return validation_results


# FastAPI middleware for automatic performance monitoring
class PerformanceMiddleware:
    """Middleware to automatically monitor API endpoint performance."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            method = scope.get("method", "")

            # Monitor work item creation endpoint
            if "/work-items" in path and method == "POST":
                async with measure_performance(
                    "api_work_item_creation", {"path": path, "method": method}
                ):
                    await self.app(scope, receive, send)
            else:
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)

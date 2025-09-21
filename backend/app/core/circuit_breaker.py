"""Circuit breaker pattern implementation."""

import time
from enum import Enum
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


class CircuitBreakerError(Exception):
    """Raised when circuit is open and operation is blocked."""

    pass


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Not allowing requests
    HALF_OPEN = "half_open"  # Testing if service is healthy


class CircuitBreaker:
    """Circuit breaker for protecting external service calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        name: str = "default",
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            name: Name for identifying this circuit breaker instance
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None

    async def __aenter__(self) -> "CircuitBreaker":
        """Context manager enter."""
        await self._check_state()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        if exc_type is not None:
            await self._handle_failure()
        else:
            await self._handle_success()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state

    async def _check_state(self) -> None:
        """Check if requests should be allowed through.

        Raises:
            HTTPException: If circuit is open
        """
        if self._state == CircuitState.OPEN:
            if await self._should_attempt_recovery():
                logger.info(
                    "Circuit entering half-open state",
                    circuit=self.name,
                )
                self._state = CircuitState.HALF_OPEN
            else:
                logger.warning(
                    "Circuit is open",
                    circuit=self.name,
                    recovery_in=self._time_until_recovery(),
                )
                raise CircuitBreakerError("Service temporarily unavailable")

    async def _handle_failure(self) -> None:
        """Handle a failed request."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            logger.warning(
                "Circuit reopened after failed recovery attempt",
                circuit=self.name,
            )
            self._state = CircuitState.OPEN
            return

        if self._failure_count >= self.failure_threshold:
            logger.warning(
                "Circuit opened after failure threshold reached",
                circuit=self.name,
                failures=self._failure_count,
            )
            self._state = CircuitState.OPEN

    async def _handle_success(self) -> None:
        """Handle a successful request."""
        if self._state == CircuitState.HALF_OPEN:
            logger.info(
                "Circuit closed after successful recovery",
                circuit=self.name,
            )
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._last_failure_time = None

    async def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if not self._last_failure_time:
            return True
        return time.time() - self._last_failure_time >= self.recovery_timeout

    def _time_until_recovery(self) -> float:
        """Calculate seconds until next recovery attempt."""
        if not self._last_failure_time:
            return 0
        elapsed = time.time() - self._last_failure_time
        return max(0, self.recovery_timeout - elapsed)

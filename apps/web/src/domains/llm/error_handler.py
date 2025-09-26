import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable, TypeVar, Awaitable
from pydantic import BaseSettings, Field
from prometheus_client import Counter, Gauge

T = TypeVar('T')

class CircuitBreakerSettings(BaseSettings):
    """Circuit breaker configuration settings."""
    failure_threshold: int = Field(5, env='LLM_CB_FAILURE_THRESHOLD')
    reset_timeout: int = Field(300, env='LLM_CB_RESET_TIMEOUT')  # 5 minutes
    half_open_timeout: int = Field(60, env='LLM_CB_HALF_OPEN_TIMEOUT')
    retry_max_attempts: int = Field(3, env='LLM_RETRY_MAX_ATTEMPTS')
    retry_initial_delay: float = Field(1.0, env='LLM_RETRY_INITIAL_DELAY')
    retry_max_delay: float = Field(10.0, env='LLM_RETRY_MAX_DELAY')
    retry_jitter: float = Field(0.1, env='LLM_RETRY_JITTER')

    class Config:
        env_file = '.env'

class CircuitBreakerState:
    """Circuit breaker state tracking."""
    CLOSED = 'closed'
    OPEN = 'open'
    HALF_OPEN = 'half-open'

class CircuitBreaker:
    """Circuit breaker pattern implementation."""

    def __init__(
        self,
        settings: CircuitBreakerSettings = CircuitBreakerSettings()
    ):
        self.settings = settings
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None

        # Metrics
        self.failures = Counter(
            'llm_circuit_breaker_failures_total',
            'Total circuit breaker failures',
            ['provider']
        )
        self.state_gauge = Gauge(
            'llm_circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=half-open, 2=open)',
            ['provider']
        )

    def _should_reset(self) -> bool:
        """Check if circuit breaker should reset."""
        if not self.last_failure_time:
            return False
        reset_time = self.last_failure_time + timedelta(
            seconds=self.settings.reset_timeout
        )
        return datetime.now() >= reset_time

    def _update_state_metric(self, provider: str) -> None:
        """Update state metric."""
        state_value = {
            CircuitBreakerState.CLOSED: 0,
            CircuitBreakerState.HALF_OPEN: 1,
            CircuitBreakerState.OPEN: 2
        }[self.state]
        self.state_gauge.labels(provider=provider).set(state_value)

    async def execute(
        self,
        provider: str,
        func: Callable[..., Awaitable[T]],
        *args: Any,
        **kwargs: Any
    ) -> T:
        """Execute function with circuit breaker pattern."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                self._update_state_metric(provider)
            else:
                raise RuntimeError("Circuit breaker is open")

        try:
            result = await self._execute_with_retry(
                provider,
                func,
                *args,
                **kwargs
            )

            # Success handling
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
                self._update_state_metric(provider)
            self.failure_count = 0
            self.last_success_time = datetime.now()

            return result

        except Exception as e:
            # Failure handling
            self.failure_count += 1
            self.failures.labels(provider=provider).inc()
            self.last_failure_time = datetime.now()

            if (
                self.failure_count >= self.settings.failure_threshold or
                self.state == CircuitBreakerState.HALF_OPEN
            ):
                self.state = CircuitBreakerState.OPEN
                self._update_state_metric(provider)

            raise e

    async def _execute_with_retry(
        self,
        provider: str,
        func: Callable[..., Awaitable[T]],
        *args: Any,
        **kwargs: Any
    ) -> T:
        """Execute with exponential backoff retry."""
        attempt = 0
        while True:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                attempt += 1
                if attempt >= self.settings.retry_max_attempts:
                    raise e

                # Calculate delay with exponential backoff and jitter
                delay = min(
                    self.settings.retry_initial_delay * (2 ** (attempt - 1)),
                    self.settings.retry_max_delay
                )
                jitter = delay * self.settings.retry_jitter
                actual_delay = delay + (jitter * (2 * asyncio.random() - 1))

                await asyncio.sleep(actual_delay)

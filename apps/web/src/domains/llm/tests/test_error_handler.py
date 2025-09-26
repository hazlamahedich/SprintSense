import pytest
from unittest.mock import AsyncMock
import asyncio
from datetime import datetime, timedelta

from ..error_handler import (
    CircuitBreaker,
    CircuitBreakerSettings,
    CircuitBreakerState
)

@pytest.fixture
def circuit_breaker():
    return CircuitBreaker(CircuitBreakerSettings(
        failure_threshold=2,
        reset_timeout=1,  # 1 second for testing
        half_open_timeout=1,
        retry_max_attempts=2,
        retry_initial_delay=0.1,
        retry_max_delay=0.5,
        retry_jitter=0.1
    ))

@pytest.fixture
def success_function():
    async def func(*args, **kwargs):
        return "success"
    return AsyncMock(side_effect=func)

@pytest.fixture
def failing_function():
    async def func(*args, **kwargs):
        raise ValueError("test error")
    return AsyncMock(side_effect=func)

@pytest.mark.asyncio
async def test_circuit_breaker_success(circuit_breaker, success_function):
    result = await circuit_breaker.execute(
        "test-provider",
        success_function,
        "arg1",
        kwarg1="value1"
    )
    
    assert result == "success"
    assert circuit_breaker.state == CircuitBreakerState.CLOSED
    assert circuit_breaker.failure_count == 0
    success_function.assert_called_once_with("arg1", kwarg1="value1")

@pytest.mark.asyncio
async def test_circuit_breaker_failure_threshold(circuit_breaker, failing_function):
    # First failure
    with pytest.raises(ValueError):
        await circuit_breaker.execute("test-provider", failing_function)
    assert circuit_breaker.state == CircuitBreakerState.CLOSED
    assert circuit_breaker.failure_count == 1
    
    # Second failure - should open circuit
    with pytest.raises(ValueError):
        await circuit_breaker.execute("test-provider", failing_function)
    assert circuit_breaker.state == CircuitBreakerState.OPEN
    assert circuit_breaker.failure_count == 2
    
    # Attempt while open - should fail fast
    with pytest.raises(RuntimeError) as exc:
        await circuit_breaker.execute("test-provider", failing_function)
    assert str(exc.value) == "Circuit breaker is open"
    assert failing_function.call_count == 2  # No additional call

@pytest.mark.asyncio
async def test_circuit_breaker_half_open(circuit_breaker, success_function):
    # Open the circuit
    circuit_breaker.state = CircuitBreakerState.OPEN
    circuit_breaker.last_failure_time = datetime.now() - timedelta(seconds=2)
    
    # Should transition to half-open and succeed
    result = await circuit_breaker.execute(
        "test-provider",
        success_function
    )
    assert result == "success"
    assert circuit_breaker.state == CircuitBreakerState.CLOSED
    assert circuit_breaker.failure_count == 0

@pytest.mark.asyncio
async def test_retry_with_backoff(circuit_breaker):
    call_count = 0
    
    async def flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("temporary error")
        return "success"
    
    result = await circuit_breaker.execute(
        "test-provider",
        flaky_function
    )
    
    assert result == "success"
    assert call_count == 2
    assert circuit_breaker.state == CircuitBreakerState.CLOSED

@pytest.mark.asyncio
async def test_max_retries_exceeded(circuit_breaker, failing_function):
    start_time = asyncio.get_event_loop().time()
    
    with pytest.raises(ValueError):
        await circuit_breaker.execute(
            "test-provider",
            failing_function
        )
    
    duration = asyncio.get_event_loop().time() - start_time
    assert failing_function.call_count == 2  # Initial + 1 retry
    assert 0.1 <= duration <= 0.3  # Check retry delay
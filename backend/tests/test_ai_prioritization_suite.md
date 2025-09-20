# AI Prioritization Test Suite

This document describes the comprehensive test suite for the AI Prioritization Service, covering unit tests, integration tests, and performance tests.

## Test Structure

```
tests/
├── unit/
│   └── services/
│       └── test_ai_prioritization_service.py  # Unit tests for service logic
├── integration/
│   └── api/
│       └── test_ai_prioritization_api.py      # API endpoint integration tests
└── performance/
    └── test_ai_prioritization_performance.py  # Performance and load tests
```

## Test Coverage

### Unit Tests (`test_ai_prioritization_service.py`)
- **TextProcessor**: HTML stripping, text normalization, keyword extraction, stemming
- **CircuitBreaker**: State management, failure tracking, recovery behavior
- **AIPrioritizationService**: Core service functionality including:
  - Work item scoring algorithm
  - Redis caching (hit/miss scenarios)
  - Authorization checks
  - Error handling
  - Business metrics calculation
  - Confidence level calculation
  - Explanation generation

### Integration Tests (`test_ai_prioritization_api.py`)
- **API Endpoints**: Full HTTP request/response cycle testing
- **Authentication**: User authorization and team membership validation
- **Database Integration**: Real database operations with test fixtures
- **Error Handling**: HTTP status codes and error responses
- **Request Validation**: Pydantic schema validation
- **Large Dataset Handling**: Scalability with many work items

### Performance Tests (`test_ai_prioritization_performance.py`)
- **Latency Requirements**: <500ms response time validation
- **Caching Performance**: Redis performance improvements
- **Concurrent Load**: Multi-request performance under load
- **Memory Efficiency**: Memory usage with large datasets
- **Algorithm Performance**: Core scoring algorithm benchmarks
- **Mode Comparison**: Fast vs Full mode performance differences

## Running the Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Optional: For memory monitoring in performance tests
pip install psutil
```

### Running Individual Test Suites

```bash
# Unit tests
pytest tests/unit/services/test_ai_prioritization_service.py -v

# Integration tests
pytest tests/integration/api/test_ai_prioritization_api.py -v

# Performance tests
pytest tests/performance/test_ai_prioritization_performance.py -v
```

### Running All AI Prioritization Tests

```bash
# Run all AI prioritization tests
pytest -k "ai_prioritization" -v

# Run with coverage report
pytest -k "ai_prioritization" --cov=app.domains.services.ai_prioritization_service --cov=app.domains.routers.ai_prioritization --cov-report=html
```

### Running Performance Tests Specifically

```bash
# Run only performance tests with detailed output
pytest tests/performance/ -v -s

# Run performance tests with specific markers
pytest -m "performance" -v
```

## Test Configuration

### Environment Variables
```bash
# For testing
export DATABASE_URL="postgresql+asyncpg://test_user:test_pass@localhost/test_db"
export REDIS_URL="redis://localhost:6379/1"
export SECRET_KEY="test-secret-key-for-jwt"
```

### Database Setup for Integration Tests
```bash
# Create test database
createdb sprintsense_test

# Run migrations
alembic upgrade head
```

## Performance Requirements

### Latency Targets
- **<500ms**: Primary response time requirement for scoring requests
- **<400ms**: Average response time under concurrent load
- **<10ms**: Per work item scoring algorithm execution
- **<50ms**: Text processing operations

### Caching Performance
- **>10%**: Minimum performance improvement with Redis caching
- **>20%**: Fast mode performance improvement over full mode

### Memory Efficiency  
- **<100MB**: Memory increase when processing 500 work items
- **Consistent**: Low variance in memory usage across requests

## Test Data

### Test Fixtures
- **Small Dataset**: 3 work items, 2 project goals
- **Large Dataset**: 100 work items, 10 project goals (performance testing)
- **Extra Large Dataset**: 500 work items, 20 project goals (stress testing)

### Mock Data Characteristics
- **Realistic Content**: Technical descriptions with relevant keywords
- **Varied Priorities**: Different priority levels for scoring validation
- **Mixed Statuses**: Various work item statuses and types
- **Keyword Diversity**: Multiple keyword patterns for matching tests

## Circuit Breaker Testing

The circuit breaker implementation is tested for:
- **Closed State**: Normal operation with successful requests
- **Failure Tracking**: Proper counting of consecutive failures
- **Open State**: Circuit opens after threshold reached
- **Recovery**: Automatic recovery after timeout period

## Error Scenarios Covered

### Authorization Errors
- Non-team member access attempts
- Invalid team IDs
- Missing authentication

### Database Errors
- Connection failures
- Query timeouts
- Transaction rollbacks

### Validation Errors
- Invalid request payloads
- Malformed UUIDs
- Out-of-range values

### Performance Degradation
- Redis connection failures with fallback
- Large dataset processing
- Concurrent request handling

## Continuous Integration

### GitHub Actions Configuration
```yaml
- name: Run AI Prioritization Tests
  run: |
    pytest tests/unit/services/test_ai_prioritization_service.py
    pytest tests/integration/api/test_ai_prioritization_api.py
    pytest tests/performance/test_ai_prioritization_performance.py --maxfail=1
```

### Pre-commit Hooks
```bash
# Install pre-commit hook to run tests
pre-commit install

# Run tests before commit
pytest -k "ai_prioritization" --maxfail=3
```

## Monitoring and Metrics

Tests validate the following metrics are properly calculated:
- **Accuracy Score**: Algorithm effectiveness measurement
- **Coverage Percentage**: Items successfully scored
- **Algorithm Version**: Version tracking for A/B testing
- **Generation Time**: Response time tracking
- **Confidence Levels**: High/Medium/Low confidence distribution

## Troubleshooting

### Common Issues

1. **Redis Connection**: Ensure Redis is running for caching tests
2. **Database Setup**: Verify test database exists and is accessible
3. **Memory Tests**: Install `psutil` for memory monitoring tests
4. **Async Issues**: Ensure proper `pytest-asyncio` configuration

### Performance Test Failures

1. **Latency Violations**: Check system load and database performance
2. **Cache Misses**: Verify Redis configuration and connectivity
3. **Memory Leaks**: Monitor for uncleaned resources between tests

### Debug Mode
```bash
# Run tests with debug output
pytest -k "ai_prioritization" -v -s --tb=long

# Run specific failing test
pytest tests/unit/services/test_ai_prioritization_service.py::TestAIPrioritizationService::test_score_work_items_success -vvv
```

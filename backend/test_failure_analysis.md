# Test Failure Analysis

## 1. Authentication Client Issues
### Test: Multiple authentication-related tests in integration tests
### Error: 
```python
AttributeError: 'FixtureFunctionDefinition' object has no attribute 'dependency_overrides'
```
### Dependencies:
- `app` fixture
- `AsyncClient`
- `authenticated_async_client` fixture
- FastAPI dependency override system

### Proposed Fix:
Issue is in the `authenticated_async_client` fixture where `app` is incorrectly referenced. The fixture should use the FastAPI app instance from the app fixture.

Fix in conftest.py:
```python
@pytest_asyncio.fixture
async def authenticated_async_client(db_session: AsyncSession, authenticated_user, app):  # Add app parameter
    from datetime import timedelta
    from app.core.security import create_access_token

    access_token = create_access_token(
        data={"sub": str(authenticated_user.id), "email": authenticated_user.email},
        expires_delta=timedelta(minutes=30),
    )

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session  # Now app is properly referenced

    async with AsyncClient(app=app, base_url="http://test", cookies={"access_token": access_token}) as ac:
        yield ac

    app.dependency_overrides.clear()
```

## 2. Test Database Session Issues
### Test: test_get_team tests and related tests
### Error:
```
fixture 'test_db_session' not found
```
### Dependencies:
- AsyncSession
- SQLAlchemy engine
- Database fixtures

### Proposed Fix:
The tests are looking for `test_db_session` but the fixture is named `db_session`. Rename references or update fixture name for consistency.

## 3. BCrypt Version Reading Issue
### Warning:
```
WARNING passlib.handlers.bcrypt:bcrypt.py:622 (trapped) error reading bcrypt version
```
### Dependencies:
- passlib
- bcrypt package

### Impact:
This is a non-blocking warning that doesn't cause test failures but should be addressed for cleaner test output.

### Proposed Fix:
Update passlib and bcrypt package versions, or add a version attribute to the bcrypt module:
```python
# Add to app initialization
import bcrypt
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("", (), {"__version__": bcrypt.__version__})()
```

## 4. Project Goals API Tests
### Test: Project goals API tests (6 failures)
### Error: Multiple failures in test_project_goals_api.py
### Dependencies:
- Project goals endpoints
- Authentication
- Database session

### Proposed Fix:
Need to investigate specific failures in the project goals tests after fixing the authentication and session issues first.

## 5. Circuit Breaker Behavior in Chaos Tests
### Test: test_quality_metrics_chaos.py
### Behavior: Some failing/passed tests with circuit breaker activation
### Dependencies:
- CircuitBreaker implementation
- Quality metrics service
- Error handling

### Notes:
This may be expected behavior as part of chaos testing, but should verify the circuit breaker thresholds and recovery times are set correctly.
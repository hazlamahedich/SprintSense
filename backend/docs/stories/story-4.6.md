# Story 4.6: Authentication and Authorization Test Fixes

## Description
Multiple test failures were discovered in the authentication, authorization, and team member access checks. These failures affected token verification, team member access, and API endpoint tests. This story documents the fixes implemented to resolve these issues.

## Changes Made

### 1. Token Verification Bug Fix
- **File**: `app/core/auth.py`
- **Issue**: Token verification was using incorrect variable, failing to check Authorization header tokens
- **Fix**: Changed `verify_token(access_token)` to `verify_token(token)` to properly handle tokens from both cookie and Authorization header
- **Impact**: Resolved authentication test failures in various API endpoints

### 2. Team Service Enhancement
- **File**: `app/domains/services/team_service.py` 
- **Added Method**: `is_user_team_member`
```python
async def is_user_team_member(self, team_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """Check if user is a member of the specified team."""
    result = await self.db_session.execute(
        select(TeamMember).where(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
            )
        )
    )
    team_member = result.scalars().first()
    return team_member is not None
```
- **Impact**: Added proper team membership validation for API endpoints

### 3. Project Goals API Test Fixes
- **File**: `tests/test_project_goals_api.py`
- **Fixes**:
  - Added missing `unittest.mock.patch` import
  - Implemented proper auth dependency patching in tests
  - Fixed test setup to use consistent auth mocking pattern

### 4. User Profile API Enhancement
- **File**: `app/api/v1/endpoints/users.py`
- **Endpoint**: `/api/v1/users/me`
- **Change**: Added proper handling of unimplemented feature case
```python
async def get_current_user_profile(current_user = Depends(get_current_user)) -> UserResponse:
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Not yet implemented"
        )
    return UserResponse.model_validate(current_user)
```

### 5. Pytest Async Configuration
- **File**: `pyproject.toml`
- **Added**: Strict asyncio mode configuration
```toml
[tool.pytest.ini_options]
asyncio_mode = "strict"
```
- **Impact**: Proper handling of async tests across the suite

## Test Results
- Total Tests: 220
- Passed: 219
- Skipped: 1
- Failed: 0

## QA Status: ✅ Passed
All tests are now passing with the implemented fixes. The changes have improved the robustness of:
- Token verification
- Team member access control
- API endpoint error handling
- Test infrastructure configuration

## Notes
- The fixes maintain backward compatibility
- No database schema changes were required
- Test coverage has been maintained
- All changes follow existing coding standards and patterns

## Related Issues
- Fixed auth token verification in multiple test scenarios
- Resolved team member access check failures
- Fixed failing project goals API tests
- Improved async test configuration

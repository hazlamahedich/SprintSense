# SPRINT-135: Fix RBAC Test Suite

## Overview
During QA review of Story 8.3 (Security and Compliance Implementation), we discovered 5 failing tests in the RBAC module. These tests need to be fixed to ensure proper authentication, rate limiting, and usage tracking behavior.

## Status
- Priority: High
- Type: Bug
- Related Story: 8.3 (Security Compliance)
- Assignee: TBD

## Test Coverage Analysis
Current RBAC module coverage: 82%
Target coverage: 85%+

## Failed Tests
1. `test_check_quota_rate_limit`
   - Expected to raise HTTPException
   - Currently not enforcing rate limits correctly
   - Fix needs to address rate limit checking logic

2. `test_middleware_requires_auth`
   - Authentication error not being caught correctly
   - Middleware failing to handle unauthenticated requests properly
   - Need to fix authentication flow in tests

3. `test_middleware_checks_permissions`
   - Authentication error hiding permission check
   - Need to properly mock authenticated state before permission check

4. `test_middleware_allows_access`
   - Same authentication issue as above
   - Need to fix test setup to include proper auth context

5. `test_middleware_tracks_usage`
   - Usage tracking not being tested due to auth failure
   - Need to ensure tracking occurs after successful auth

## Required Fixes

### Rate Limiting Test
1. Ensure test properly sets up Redis mock
2. Verify rate limit counter is being incremented
3. Add proper test configuration for rate limits
4. Add test for rate limit reset

### Middleware Tests
1. Add proper authentication context to test client
2. Mock state.user_id and state.team_id correctly
3. Fix test setup to include all required dependencies
4. Add better error handling assertions

### Usage Tracking
1. Verify Redis pipeline usage for tracking
2. Add test coverage for failed tracking scenarios
3. Ensure proper cleanup between tests

## Acceptance Criteria
- [ ] All 5 failing tests pass consistently
- [ ] Test coverage for RBAC module increases to 85%+
- [ ] No regressions in other security tests
- [ ] Properly mocked dependencies throughout test suite
- [ ] Clear documentation for test requirements

## Dependencies
- FastAPI TestClient for integration tests
- Redis mocking
- SQLAlchemy test database
- Authentication middleware

## Notes
- Consider refactoring test setup to use shared fixtures
- May need to update RBAC implementation based on test findings
- Review similar middleware tests in other modules for patterns
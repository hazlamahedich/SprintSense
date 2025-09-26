# Authentication

This document describes the authentication methods supported by the SprintSense API.

## Overview

The API supports two authentication methods:
1. Cookie-based authentication (recommended for web browsers)
2. Bearer token authentication (recommended for non-browser clients)

## Authentication Methods

### Cookie Authentication

After login, the server sets an HTTP-only cookie named `access_token`. This is the preferred method for web browser clients as it provides better security against XSS attacks.

Example login that sets the cookie:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secretpassword"}' \
  -c cookies.txt  # Save cookies to file
```

Subsequent requests will automatically include the cookie:
```bash
curl http://localhost:8000/api/v1/users/me \
  -b cookies.txt  # Use saved cookies
```

### Bearer Token Authentication

For non-browser clients, you can use Bearer token authentication by including the token in the Authorization header.

Example login to get token:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secretpassword"}'

# Response includes access_token
```

Using the token in subsequent requests:
```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Token Format

The access token is a JWT (JSON Web Token) that includes:
- Subject (`sub`): User ID
- Email (`email`): User's email address
- Expiration (`exp`): Token expiration timestamp

## Error Responses

Authentication errors return 401 Unauthorized with details:

```json
{
  "detail": {
    "error": "invalid_token",
    "error_description": "Could not validate credentials"
  }
}
```

Common error cases:
- Missing token: No access token provided in cookie or Authorization header
- Invalid token: Token format is incorrect or signature is invalid
- Expired token: Token has passed its expiration time
- User not found: Token contains invalid user ID
- Inactive user: User account is disabled

## Security Considerations

1. Always use HTTPS in production
2. Tokens are short-lived (default 30 minutes)
3. HTTP-only cookies are used to prevent XSS access to tokens
4. Bearer tokens should be transmitted securely and never stored in client-side storage
5. Implement proper token rotation and logout handling

## Example Implementation

TypeScript/JavaScript example using both auth methods:

```typescript
// Cookie auth (browser)
async function loginWithCookie() {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    credentials: 'include',  // Important for cookies
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: 'user@example.com',
      password: 'password123',
    }),
  });
}

// Bearer token auth (non-browser)
async function loginWithToken() {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: 'user@example.com',
      password: 'password123',
    }),
  });
  const { access_token } = await response.json();
  
  // Use token in subsequent requests
  const userResponse = await fetch('/api/v1/users/me', {
    headers: {
      'Authorization': `Bearer ${access_token}`,
    },
  });
}
```

## Breaking Changes

The following changes were made to the authentication system:
1. Added support for Bearer token authentication
2. Modified token validation to check both cookie and Authorization header
3. Updated error messages to be more specific about auth failure reasons

Update your clients to:
1. Use either cookie or Bearer token auth consistently
2. Handle more specific error messages
3. Implement proper token storage based on client type

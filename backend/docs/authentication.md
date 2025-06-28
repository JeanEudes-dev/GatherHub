# GatherHub API Authentication Guide

## Overview

GatherHub uses JWT (JSON Web Token) based authentication for secure API access. This guide covers all authentication-related endpoints and best practices.

## Authentication Flow

### 1. User Registration

**Endpoint**: `POST /api/v1/auth/register/`

Register a new user account:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "name": "John Doe"
  }'
```

**Response**:

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "message": "User registered successfully."
}
```

### 2. User Login

**Endpoint**: `POST /api/v1/auth/token/`

Authenticate existing user:

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

**Response**:

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 3. Token Refresh

**Endpoint**: `POST /api/v1/auth/token/refresh/`

Refresh access token using refresh token:

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }'
```

**Response**:

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Using Authentication Tokens

### Including Tokens in Requests

For all authenticated endpoints, include the access token in the Authorization header:

```bash
curl -X GET http://localhost:8000/api/v1/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### JavaScript Example

```javascript
// Store tokens after login
const tokens = response.data.tokens;
localStorage.setItem("access_token", tokens.access);
localStorage.setItem("refresh_token", tokens.refresh);

// Make authenticated requests
const api = axios.create({
  baseURL: "http://localhost:8000/api/v1/",
  headers: {
    Authorization: `Bearer ${localStorage.getItem("access_token")}`,
  },
});

// Auto-refresh token on 401 responses
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      try {
        const refreshResponse = await axios.post("/auth/token/refresh/", {
          refresh: localStorage.getItem("refresh_token"),
        });

        const newToken = refreshResponse.data.access;
        localStorage.setItem("access_token", newToken);

        // Retry original request
        error.config.headers.Authorization = `Bearer ${newToken}`;
        return axios.request(error.config);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);
```

## Security Best Practices

### Token Management

1. **Store Tokens Securely**:

   - Use httpOnly cookies for web applications
   - Use secure storage for mobile apps
   - Never store tokens in localStorage for production

2. **Token Lifecycle**:

   - Access tokens expire in 60 minutes (production: 15 minutes)
   - Refresh tokens expire in 7 days (production: 1 day)
   - Always handle token expiration gracefully

3. **Logout**:
   - Clear tokens from client storage
   - Use token blacklisting endpoint (coming soon)

### Password Requirements

- Minimum 8 characters
- Cannot be too similar to personal information
- Cannot be a commonly used password
- Cannot be entirely numeric

### Rate Limiting

Authentication endpoints have strict rate limits:

- **Registration**: 5 requests per minute per IP
- **Login**: 5 requests per minute per IP
- **Token Refresh**: 10 requests per minute per user
- **Password Change**: 5 requests per minute per user

## Error Handling

### Common Authentication Errors

**401 Unauthorized**:

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden**:

```json
{
  "detail": "You do not have permission to perform this action."
}
```

**429 Rate Limit Exceeded**:

```json
{
  "error": "Rate limit exceeded",
  "detail": "Too many requests. Please try again later.",
  "type": "auth"
}
```

**400 Bad Request** (Invalid credentials):

```json
{
  "detail": "No active account found with the given credentials"
}
```

## Profile Management

### Get User Profile

**Endpoint**: `GET /api/v1/profile/`

```bash
curl -X GET http://localhost:8000/api/v1/profile/ \
  -H "Authorization: Bearer your_access_token"
```

### Update Profile

**Endpoint**: `PUT /api/v1/profile/`

```bash
curl -X PUT http://localhost:8000/api/v1/profile/ \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name"
  }'
```

### Change Password

**Endpoint**: `POST /api/v1/auth/password/change/`

```bash
curl -X POST http://localhost:8000/api/v1/auth/password/change/ \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "currentpass123",
    "new_password": "newpassword456"
  }'
```

### Upload Avatar

**Endpoint**: `PUT /api/v1/profile/`

```bash
curl -X PUT http://localhost:8000/api/v1/profile/ \
  -H "Authorization: Bearer your_access_token" \
  -F "avatar=@/path/to/image.jpg"
```

## Testing Authentication

### Using curl

```bash
# Register
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "name": "Test User"
  }')

# Extract access token
ACCESS_TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.tokens.access')

# Make authenticated request
curl -X GET http://localhost:8000/api/v1/profile/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Using Python requests

```python
import requests

# Register user
register_data = {
    'email': 'test@example.com',
    'password': 'testpass123',
    'name': 'Test User'
}

response = requests.post(
    'http://localhost:8000/api/v1/auth/register/',
    json=register_data
)

tokens = response.json()['tokens']

# Make authenticated request
headers = {'Authorization': f"Bearer {tokens['access']}"}
profile_response = requests.get(
    'http://localhost:8000/api/v1/profile/',
    headers=headers
)

print(profile_response.json())
```

## Troubleshooting

### Common Issues

1. **Token Expired**:

   - Use refresh token to get new access token
   - Check token expiration time

2. **Invalid Token Format**:

   - Ensure "Bearer " prefix is included
   - Check for extra spaces or characters

3. **Rate Limiting**:

   - Wait before retrying
   - Implement exponential backoff

4. **CORS Issues**:
   - Check allowed origins in settings
   - Ensure proper headers are sent

### Debug Mode

In development, you can inspect JWT tokens at [jwt.io](https://jwt.io) to debug token contents and expiration times.

Remember: Never share or inspect production tokens on external websites!

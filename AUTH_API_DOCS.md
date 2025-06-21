# GatherHub Authentication API Documentation

## Overview

The GatherHub Authentication API provides a comprehensive JWT-based authentication system with user management features. This API handles user registration, login, profile management, avatar uploads, and password changes.

## Base URL

```
http://127.0.0.1:8001/api/v1/auth/
```

## Authentication

All protected endpoints require a JWT access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Endpoints

### 1. User Registration

**POST** `/register/`

Register a new user account with email and password.

**Permission:** `AllowAny`

**Request Body:**

```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepass123",
  "password_confirm": "securepass123"
}
```

**Response (201 Created):**

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  },
  "tokens": {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "message": "User registered successfully."
}
```

**Validation Rules:**

- Email must be valid format and unique
- Password must be at least 8 characters
- Password must contain letters and numbers
- Password confirmation must match

---

### 2. User Login

**POST** `/token/`

Authenticate user and obtain JWT tokens.

**Permission:** `AllowAny`

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response (200 OK):**

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 3. Token Refresh

**POST** `/token/refresh/`

Refresh an expired access token using a refresh token.

**Permission:** `AllowAny`

**Request Body:**

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 4. Token Verification

**POST** `/token/verify/`

Verify if a token is valid.

**Permission:** `AllowAny`

**Request Body:**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**

```json
{}
```

---

### 5. Get User Profile

**GET** `/profile/`

Retrieve current authenticated user's profile information.

**Permission:** `IsAuthenticated`

**Response (200 OK):**

```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "avatar": "http://127.0.0.1:8001/media/avatars/avatar.jpg",
  "avatar_url": "http://127.0.0.1:8001/media/avatars/avatar.jpg",
  "date_joined": "2025-06-21T20:00:00Z",
  "last_login": "2025-06-21T20:30:00Z"
}
```

---

### 6. Update User Profile

**PUT** `/profile/`

Update current authenticated user's profile (name and avatar).

**Permission:** `IsAuthenticated`

**Request Body (JSON or multipart/form-data):**

```json
{
  "name": "Updated Name"
}
```

**For avatar upload (multipart/form-data):**

```
Content-Type: multipart/form-data

name: "Updated Name"
avatar: [image file]
```

**Response (200 OK):**

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "Updated Name",
    "avatar": "http://127.0.0.1:8001/media/avatars/new_avatar.jpg",
    "avatar_url": "http://127.0.0.1:8001/media/avatars/new_avatar.jpg",
    "date_joined": "2025-06-21T20:00:00Z",
    "last_login": "2025-06-21T20:30:00Z"
  },
  "message": "Profile updated successfully."
}
```

**Avatar Validation:**

- File size: Maximum 5MB
- Allowed formats: JPEG, PNG
- File extensions: .jpg, .jpeg, .png

---

### 7. Delete Avatar

**DELETE** `/profile/avatar/`

Delete current authenticated user's avatar.

**Permission:** `IsAuthenticated`

**Response (200 OK):**

```json
{
  "message": "Avatar deleted successfully."
}
```

**Response (400 Bad Request) - No avatar to delete:**

```json
{
  "message": "No avatar to delete."
}
```

---

### 8. Change Password

**POST** `/change-password/`

Change current authenticated user's password.

**Permission:** `IsAuthenticated`

**Request Body:**

```json
{
  "current_password": "currentpass123",
  "new_password": "newpass123",
  "new_password_confirm": "newpass123"
}
```

**Response (200 OK):**

```json
{
  "message": "Password changed successfully."
}
```

**Validation Rules:**

- Current password must be correct
- New password must be at least 8 characters
- New password must contain letters and numbers
- New password confirmation must match
- New password must be different from current password

---

## Error Responses

### 400 Bad Request

```json
{
  "field_name": ["Error message for this field."]
}
```

### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 401 Unauthorized (Invalid Token)

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "detail": "A server error occurred."
}
```

---

## Security Features

### Password Validation

- Minimum 8 characters
- Must contain letters and numbers
- Checked against common passwords
- Cannot be too similar to user information

### Email Validation

- Proper email format validation
- Uniqueness enforcement
- Case-insensitive storage

### JWT Token Security

- Access tokens expire after 60 minutes
- Refresh tokens expire after 7 days
- Secure token generation and validation

### Avatar Upload Security

- File type validation (JPEG/PNG only)
- File size limits (5MB maximum)
- Secure file storage in media directory

---

## Rate Limiting Recommendations

For production deployment, consider implementing rate limiting:

- Registration: 5 attempts per hour per IP
- Login: 10 attempts per hour per IP
- Password change: 3 attempts per hour per user

---

## Usage Examples

### Register and Login Flow

```bash
# 1. Register new user
curl -X POST http://127.0.0.1:8001/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "securepass123",
    "password_confirm": "securepass123"
  }'

# 2. Use tokens from registration response or login
curl -X POST http://127.0.0.1:8001/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

### Profile Management

```bash
# Get profile
curl -X GET http://127.0.0.1:8001/api/v1/auth/profile/ \
  -H "Authorization: Bearer <access_token>"

# Update profile with avatar
curl -X PUT http://127.0.0.1:8001/api/v1/auth/profile/ \
  -H "Authorization: Bearer <access_token>" \
  -F "name=Updated Name" \
  -F "avatar=@/path/to/image.jpg"
```

### Token Management

```bash
# Refresh token
curl -X POST http://127.0.0.1:8001/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<refresh_token>"
  }'

# Verify token
curl -X POST http://127.0.0.1:8001/api/v1/auth/token/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "<access_token>"
  }'
```

---

## Integration Notes

This authentication system is designed to work seamlessly with frontend applications. The consistent JSON response format and proper HTTP status codes make it easy to integrate with modern JavaScript frameworks like React, Vue, or Angular.

The avatar URLs returned are fully qualified URLs that can be used directly in `<img>` tags or as profile picture sources.

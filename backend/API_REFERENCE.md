# GatherHub API Reference

Complete API reference for the GatherHub Backend API. This document provides detailed information about all available endpoints, request/response formats, and authentication requirements.

## Base Information

- **Base URL**: `https://your-domain.onrender.com` (production) or `http://localhost:8000` (development)
- **API Version**: v1
- **Content Type**: `application/json`
- **Authentication**: JWT Bearer Token

## Authentication

All API endpoints (except registration and login) require authentication using JWT tokens.

### Headers

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Token Management

- **Access Token**: Valid for 1 hour
- **Refresh Token**: Valid for 7 days
- **Token Rotation**: Refresh tokens are rotated on use

---

## Authentication Endpoints

### User Registration

Register a new user account.

**Endpoint**: `POST /api/v1/auth/register/`

**Request Body**:

```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "first_name": "string",
  "last_name": "string"
}
```

**Response** (201 Created):

```json
{
  "access": "string",
  "refresh": "string",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "date_joined": "2024-01-01T12:00:00Z"
  }
}
```

**Error Responses**:

- `400 Bad Request`: Validation errors
- `409 Conflict`: Username or email already exists

### User Login

Authenticate user and receive tokens.

**Endpoint**: `POST /api/v1/auth/login/`

**Request Body**:

```json
{
  "username": "string",
  "password": "string"
}
```

**Response** (200 OK):

```json
{
  "access": "string",
  "refresh": "string",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string"
  }
}
```

**Error Responses**:

- `400 Bad Request`: Invalid credentials
- `401 Unauthorized`: Account disabled

### Token Refresh

Get a new access token using refresh token.

**Endpoint**: `POST /api/v1/auth/refresh/`

**Request Body**:

```json
{
  "refresh": "string"
}
```

**Response** (200 OK):

```json
{
  "access": "string",
  "refresh": "string"
}
```

**Error Responses**:

- `401 Unauthorized`: Invalid or expired refresh token

### User Logout

Invalidate the current refresh token.

**Endpoint**: `POST /api/v1/auth/logout/`
**Authentication**: Required

**Request Body**:

```json
{
  "refresh": "string"
}
```

**Response** (200 OK):

```json
{
  "message": "Successfully logged out"
}
```

### Get User Profile

Retrieve current user's profile information.

**Endpoint**: `GET /api/v1/auth/profile/`
**Authentication**: Required

**Response** (200 OK):

```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "bio": "string",
  "avatar": "string",
  "date_joined": "2024-01-01T12:00:00Z",
  "last_login": "2024-01-01T12:00:00Z"
}
```

### Update User Profile

Update current user's profile information.

**Endpoint**: `PUT /api/v1/auth/profile/`
**Authentication**: Required

**Request Body**:

```json
{
  "first_name": "string",
  "last_name": "string",
  "bio": "string",
  "avatar": "file"
}
```

**Response** (200 OK):

```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "bio": "string",
  "avatar": "string",
  "date_joined": "2024-01-01T12:00:00Z"
}
```

---

## Event Endpoints

### List Events

Retrieve a list of events with pagination and filtering.

**Endpoint**: `GET /api/v1/events/`
**Authentication**: Required

**Query Parameters**:

- `page` (integer): Page number
- `page_size` (integer): Items per page (max 100)
- `search` (string): Search in title and description
- `status` (string): Filter by status (`upcoming`, `ongoing`, `completed`)
- `creator` (integer): Filter by creator ID
- `date_from` (date): Filter events from date
- `date_to` (date): Filter events to date

**Response** (200 OK):

```json
{
  "count": 25,
  "next": "http://localhost:8000/api/v1/events/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "string",
      "description": "string",
      "date": "2024-01-01T12:00:00Z",
      "location": "string",
      "max_participants": 50,
      "current_participants": 15,
      "status": "upcoming",
      "creator": {
        "id": 1,
        "username": "string",
        "first_name": "string",
        "last_name": "string"
      },
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### Create Event

Create a new event.

**Endpoint**: `POST /api/v1/events/`
**Authentication**: Required

**Request Body**:

```json
{
  "title": "string",
  "description": "string",
  "date": "2024-01-01T12:00:00Z",
  "location": "string",
  "max_participants": 50
}
```

**Response** (201 Created):

```json
{
  "id": 1,
  "title": "string",
  "description": "string",
  "date": "2024-01-01T12:00:00Z",
  "location": "string",
  "max_participants": 50,
  "current_participants": 1,
  "status": "upcoming",
  "creator": {
    "id": 1,
    "username": "string",
    "first_name": "string",
    "last_name": "string"
  },
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Get Event Details

Retrieve detailed information about a specific event.

**Endpoint**: `GET /api/v1/events/{id}/`
**Authentication**: Required

**Response** (200 OK):

```json
{
  "id": 1,
  "title": "string",
  "description": "string",
  "date": "2024-01-01T12:00:00Z",
  "location": "string",
  "max_participants": 50,
  "current_participants": 15,
  "status": "upcoming",
  "creator": {
    "id": 1,
    "username": "string",
    "first_name": "string",
    "last_name": "string"
  },
  "participants": [
    {
      "id": 2,
      "username": "string",
      "first_name": "string",
      "last_name": "string"
    }
  ],
  "tasks": [
    {
      "id": 1,
      "title": "string",
      "status": "pending"
    }
  ],
  "votes": [
    {
      "id": 1,
      "title": "string",
      "status": "active"
    }
  ],
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Error Responses**:

- `404 Not Found`: Event does not exist

### Update Event

Update an existing event (creator only).

**Endpoint**: `PUT /api/v1/events/{id}/`
**Authentication**: Required
**Permissions**: Event creator only

**Request Body**:

```json
{
  "title": "string",
  "description": "string",
  "date": "2024-01-01T12:00:00Z",
  "location": "string",
  "max_participants": 50
}
```

**Response** (200 OK):

```json
{
  "id": 1,
  "title": "string",
  "description": "string",
  "date": "2024-01-01T12:00:00Z",
  "location": "string",
  "max_participants": 50,
  "current_participants": 15,
  "status": "upcoming",
  "creator": {
    "id": 1,
    "username": "string"
  },
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Error Responses**:

- `403 Forbidden`: Not the event creator
- `404 Not Found`: Event does not exist

### Delete Event

Delete an event (creator only).

**Endpoint**: `DELETE /api/v1/events/{id}/`
**Authentication**: Required
**Permissions**: Event creator only

**Response** (204 No Content)

**Error Responses**:

- `403 Forbidden`: Not the event creator
- `404 Not Found`: Event does not exist

### Join Event

Join an event as a participant.

**Endpoint**: `POST /api/v1/events/{id}/join/`
**Authentication**: Required

**Response** (200 OK):

```json
{
  "message": "Successfully joined the event",
  "event": {
    "id": 1,
    "title": "string",
    "current_participants": 16
  }
}
```

**Error Responses**:

- `400 Bad Request`: Already a participant or event is full
- `404 Not Found`: Event does not exist

### Leave Event

Leave an event (remove participation).

**Endpoint**: `POST /api/v1/events/{id}/leave/`
**Authentication**: Required

**Response** (200 OK):

```json
{
  "message": "Successfully left the event",
  "event": {
    "id": 1,
    "title": "string",
    "current_participants": 14
  }
}
```

**Error Responses**:

- `400 Bad Request`: Not a participant
- `403 Forbidden`: Event creator cannot leave
- `404 Not Found`: Event does not exist

---

## Task Endpoints

### List Tasks

Retrieve a list of tasks with filtering.

**Endpoint**: `GET /api/v1/tasks/`
**Authentication**: Required

**Query Parameters**:

- `page` (integer): Page number
- `page_size` (integer): Items per page
- `event` (integer): Filter by event ID
- `assignee` (integer): Filter by assignee ID
- `status` (string): Filter by status (`pending`, `in_progress`, `completed`)
- `due_date_from` (date): Filter tasks from due date
- `due_date_to` (date): Filter tasks to due date

**Response** (200 OK):

```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "string",
      "description": "string",
      "status": "pending",
      "priority": "medium",
      "due_date": "2024-01-01T12:00:00Z",
      "event": {
        "id": 1,
        "title": "string"
      },
      "assignee": {
        "id": 2,
        "username": "string",
        "first_name": "string",
        "last_name": "string"
      },
      "creator": {
        "id": 1,
        "username": "string"
      },
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### Create Task

Create a new task for an event.

**Endpoint**: `POST /api/v1/tasks/`
**Authentication**: Required

**Request Body**:

```json
{
  "title": "string",
  "description": "string",
  "event": 1,
  "priority": "medium",
  "due_date": "2024-01-01T12:00:00Z",
  "assignee": 2
}
```

**Response** (201 Created):

```json
{
  "id": 1,
  "title": "string",
  "description": "string",
  "status": "pending",
  "priority": "medium",
  "due_date": "2024-01-01T12:00:00Z",
  "event": {
    "id": 1,
    "title": "string"
  },
  "assignee": {
    "id": 2,
    "username": "string"
  },
  "creator": {
    "id": 1,
    "username": "string"
  },
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Get Task Details

Retrieve detailed information about a specific task.

**Endpoint**: `GET /api/v1/tasks/{id}/`
**Authentication**: Required

**Response** (200 OK):

```json
{
  "id": 1,
  "title": "string",
  "description": "string",
  "status": "pending",
  "priority": "medium",
  "due_date": "2024-01-01T12:00:00Z",
  "event": {
    "id": 1,
    "title": "string",
    "date": "2024-01-01T12:00:00Z"
  },
  "assignee": {
    "id": 2,
    "username": "string",
    "first_name": "string",
    "last_name": "string",
    "email": "string"
  },
  "creator": {
    "id": 1,
    "username": "string"
  },
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Update Task

Update an existing task.

**Endpoint**: `PUT /api/v1/tasks/{id}/`
**Authentication**: Required
**Permissions**: Task creator or assignee

**Request Body**:

```json
{
  "title": "string",
  "description": "string",
  "status": "in_progress",
  "priority": "high",
  "due_date": "2024-01-01T12:00:00Z",
  "assignee": 2
}
```

**Response** (200 OK):

```json
{
  "id": 1,
  "title": "string",
  "description": "string",
  "status": "in_progress",
  "priority": "high",
  "due_date": "2024-01-01T12:00:00Z",
  "event": {
    "id": 1,
    "title": "string"
  },
  "assignee": {
    "id": 2,
    "username": "string"
  },
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Assign Task

Assign a task to a specific user.

**Endpoint**: `POST /api/v1/tasks/{id}/assign/`
**Authentication**: Required
**Permissions**: Event creator or task creator

**Request Body**:

```json
{
  "assignee": 2
}
```

**Response** (200 OK):

```json
{
  "message": "Task assigned successfully",
  "task": {
    "id": 1,
    "title": "string",
    "assignee": {
      "id": 2,
      "username": "string"
    }
  }
}
```

### Complete Task

Mark a task as completed.

**Endpoint**: `POST /api/v1/tasks/{id}/complete/`
**Authentication**: Required
**Permissions**: Task assignee or creator

**Response** (200 OK):

```json
{
  "message": "Task marked as completed",
  "task": {
    "id": 1,
    "title": "string",
    "status": "completed",
    "completed_at": "2024-01-01T12:00:00Z"
  }
}
```

---

## Voting Endpoints

### List Votes

Retrieve a list of votes with filtering.

**Endpoint**: `GET /api/v1/voting/`
**Authentication**: Required

**Query Parameters**:

- `page` (integer): Page number
- `page_size` (integer): Items per page
- `event` (integer): Filter by event ID
- `status` (string): Filter by status (`active`, `ended`)
- `creator` (integer): Filter by creator ID

**Response** (200 OK):

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "string",
      "description": "string",
      "status": "active",
      "event": {
        "id": 1,
        "title": "string"
      },
      "creator": {
        "id": 1,
        "username": "string"
      },
      "total_votes": 15,
      "ends_at": "2024-01-01T12:00:00Z",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### Create Vote

Create a new vote for an event.

**Endpoint**: `POST /api/v1/voting/`
**Authentication**: Required

**Request Body**:

```json
{
  "title": "string",
  "description": "string",
  "event": 1,
  "options": [
    { "text": "Option 1" },
    { "text": "Option 2" },
    { "text": "Option 3" }
  ],
  "ends_at": "2024-01-01T12:00:00Z",
  "multiple_choice": false
}
```

**Response** (201 Created):

```json
{
  "id": 1,
  "title": "string",
  "description": "string",
  "status": "active",
  "event": {
    "id": 1,
    "title": "string"
  },
  "creator": {
    "id": 1,
    "username": "string"
  },
  "options": [
    {
      "id": 1,
      "text": "Option 1",
      "vote_count": 0
    },
    {
      "id": 2,
      "text": "Option 2",
      "vote_count": 0
    }
  ],
  "total_votes": 0,
  "ends_at": "2024-01-01T12:00:00Z",
  "multiple_choice": false,
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Get Vote Details

Retrieve detailed information about a specific vote.

**Endpoint**: `GET /api/v1/voting/{id}/`
**Authentication**: Required

**Response** (200 OK):

```json
{
  "id": 1,
  "title": "string",
  "description": "string",
  "status": "active",
  "event": {
    "id": 1,
    "title": "string",
    "date": "2024-01-01T12:00:00Z"
  },
  "creator": {
    "id": 1,
    "username": "string"
  },
  "options": [
    {
      "id": 1,
      "text": "Option 1",
      "vote_count": 8,
      "percentage": 53.3
    },
    {
      "id": 2,
      "text": "Option 2",
      "vote_count": 7,
      "percentage": 46.7
    }
  ],
  "total_votes": 15,
  "user_voted": true,
  "user_vote": {
    "option_id": 1,
    "voted_at": "2024-01-01T12:00:00Z"
  },
  "ends_at": "2024-01-01T12:00:00Z",
  "multiple_choice": false,
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Cast Vote

Cast a vote for specific option(s).

**Endpoint**: `POST /api/v1/voting/{id}/vote/`
**Authentication**: Required

**Request Body**:

```json
{
  "options": [1]
}
```

**Response** (200 OK):

```json
{
  "message": "Vote cast successfully",
  "vote": {
    "id": 1,
    "title": "string",
    "user_vote": {
      "option_id": 1,
      "voted_at": "2024-01-01T12:00:00Z"
    },
    "total_votes": 16
  }
}
```

**Error Responses**:

- `400 Bad Request`: Already voted or invalid options
- `403 Forbidden`: Voting ended or not authorized

### Get Vote Results

Retrieve current results of a vote.

**Endpoint**: `GET /api/v1/voting/{id}/results/`
**Authentication**: Required

**Response** (200 OK):

```json
{
  "id": 1,
  "title": "string",
  "status": "active",
  "total_votes": 15,
  "results": [
    {
      "option_id": 1,
      "text": "Option 1",
      "vote_count": 8,
      "percentage": 53.3
    },
    {
      "option_id": 2,
      "text": "Option 2",
      "vote_count": 7,
      "percentage": 46.7
    }
  ],
  "ends_at": "2024-01-01T12:00:00Z",
  "winner": {
    "option_id": 1,
    "text": "Option 1"
  }
}
```

---

## Health Endpoints

### Basic Health Check

Basic application health status.

**Endpoint**: `GET /health/`
**Authentication**: Not required

**Response** (200 OK):

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

### Readiness Check

Check if all services are ready.

**Endpoint**: `GET /health/ready/`
**Authentication**: Not required

**Response** (200 OK / 503 Service Unavailable):

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "checks": {
    "database": {
      "status": "healthy",
      "latency_ms": 5.2
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 1.1
    },
    "channels": {
      "status": "healthy",
      "latency_ms": 2.3
    }
  },
  "total_latency_ms": 8.6
}
```

### Liveness Check

Check if the application is alive.

**Endpoint**: `GET /health/live/`
**Authentication**: Not required

**Response** (200 OK / 503 Service Unavailable):

```json
{
  "status": "alive",
  "timestamp": "2024-01-01T12:00:00Z",
  "django_ready": true
}
```

### Status Dashboard

Comprehensive system status information.

**Endpoint**: `GET /health/status/`
**Authentication**: Not required

**Response** (200 OK):

```json
{
  "status": "ok",
  "timestamp": "2024-01-01T12:00:00Z",
  "uptime_check_ms": 15.3,
  "system": {
    "python_version": "3.11.0",
    "platform": "Linux",
    "django_version": "5.0.0",
    "environment": "production"
  },
  "database": {
    "status": "connected",
    "version": "PostgreSQL 15.0",
    "table_count": 25
  },
  "cache": {
    "status": "working",
    "backend": "redis"
  },
  "debug_mode": false,
  "allowed_hosts": ["your-domain.com"]
}
```

---

## Error Responses

### Standard Error Format

All API errors follow this format:

```json
{
  "error": "error_code",
  "message": "Human readable error message",
  "details": {
    "field_name": ["Field specific error message"]
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Common HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Request successful, no content to return
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or invalid
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Rate Limiting Headers

When rate limits are applied:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

Rate limit exceeded response:

```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Try again in 60 seconds.",
  "details": {
    "limit": 100,
    "window": "1 minute",
    "reset_at": "2024-01-01T12:01:00Z"
  }
}
```

---

## WebSocket API

### Connection

Connect to WebSocket endpoints using:

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/events/");
```

### Message Format

All WebSocket messages follow this format:

```json
{
  "type": "message_type",
  "data": {
    "key": "value"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Event Messages

- `event_created`: New event created
- `event_updated`: Event details updated
- `event_joined`: User joined event
- `event_left`: User left event

### Task Messages

- `task_created`: New task created
- `task_updated`: Task status updated
- `task_assigned`: Task assigned to user
- `task_completed`: Task marked as complete

### Vote Messages

- `vote_created`: New vote created
- `vote_cast`: Vote cast by user
- `vote_results`: Vote results updated
- `vote_ended`: Voting period ended

---

This API reference provides comprehensive documentation for integrating with the GatherHub Backend API. For additional examples and integration guides, see the main README.md file.

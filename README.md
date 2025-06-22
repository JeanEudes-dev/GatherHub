# GatherHub Backend API

A real-time community event planner built with Django REST Framework and WebSockets. GatherHub enables communities to organize events, manage tasks, and make collaborative decisions through an integrated voting system.

![Django](https://img.shields.io/badge/Django-5.0+-green.svg)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Redis](https://img.shields.io/badge/Redis-7+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Features

### Core Functionality

- **User Management**: Registration, authentication, and profile management
- **Event Planning**: Create, manage, and organize community events
- **Task Management**: Assign and track event-related tasks
- **Voting System**: Democratic decision-making with real-time vote tracking
- **Real-time Updates**: WebSocket-powered live notifications and updates

### Technical Features

- **RESTful API**: Comprehensive REST API with OpenAPI documentation
- **Real-time Communication**: WebSocket support for instant updates
- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: Built-in API rate limiting and security
- **Health Monitoring**: Comprehensive health checks and monitoring
- **Production Ready**: Docker containerization and cloud deployment

## 🏗️ Architecture

### Technology Stack

- **Framework**: Django 5.0+ with Django REST Framework
- **Database**: PostgreSQL 15+
- **Cache/Message Broker**: Redis 7+
- **Real-time**: Django Channels with WebSockets
- **Authentication**: JWT with SimpleJWT
- **Documentation**: OpenAPI 3.0 with Spectacular
- **Deployment**: Docker + Render.com

### Database Schema

```
Users (CustomUser)
├── Events
│   ├── Tasks
│   └── EventMembers
├── Voting
│   ├── VoteOptions
│   └── UserVotes
└── UserProfiles
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker (optional)

### Local Development Setup

#### 1. Clone and Setup

```bash
git clone https://github.com/JeanEudes-dev/GatherHub.git
cd GatherHub

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/gatherhub
REDIS_URL=redis://localhost:6379/0
```

#### 3. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

#### 4. Start Development Server

```bash
# Start Django development server
python manage.py runserver

# In another terminal, start Redis (if not running)
redis-server
```

### Docker Development Setup

#### 1. Quick Start with Docker Compose

```bash
# Clone repository
git clone https://github.com/JeanEudes-dev/GatherHub.git
cd GatherHub

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec app python manage.py migrate

# Create superuser
docker-compose exec app python manage.py createsuperuser
```

#### 2. Access the Application

- **API Base URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Interface**: http://localhost:8000/admin/
- **Health Check**: http://localhost:8000/health/

## 📚 API Documentation

### Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.onrender.com`

### Authentication

GatherHub uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### Authentication Endpoints

```http
POST /api/v1/auth/register/          # User registration
POST /api/v1/auth/login/             # User login
POST /api/v1/auth/refresh/           # Refresh JWT token
POST /api/v1/auth/logout/            # User logout
GET  /api/v1/auth/profile/           # Get user profile
PUT  /api/v1/auth/profile/           # Update user profile
```

### Event Management

```http
GET    /api/v1/events/               # List events
POST   /api/v1/events/               # Create event
GET    /api/v1/events/{id}/          # Get event details
PUT    /api/v1/events/{id}/          # Update event
DELETE /api/v1/events/{id}/          # Delete event
POST   /api/v1/events/{id}/join/     # Join event
POST   /api/v1/events/{id}/leave/    # Leave event
```

### Task Management

```http
GET    /api/v1/tasks/                # List tasks
POST   /api/v1/tasks/                # Create task
GET    /api/v1/tasks/{id}/           # Get task details
PUT    /api/v1/tasks/{id}/           # Update task
DELETE /api/v1/tasks/{id}/           # Delete task
POST   /api/v1/tasks/{id}/assign/    # Assign task
POST   /api/v1/tasks/{id}/complete/  # Mark task complete
```

### Voting System

```http
GET    /api/v1/voting/               # List votes
POST   /api/v1/voting/               # Create vote
GET    /api/v1/voting/{id}/          # Get vote details
POST   /api/v1/voting/{id}/vote/     # Cast vote
GET    /api/v1/voting/{id}/results/  # Get vote results
```

### Interactive Documentation

- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`
- **OpenAPI Schema**: `/api/schema/`

## 🔌 Real-time Features

### WebSocket Connection

Connect to WebSocket for real-time updates:

```javascript
// Connect to WebSocket
const ws = new WebSocket("ws://localhost:8000/ws/events/");

// Handle connection
ws.onopen = function (event) {
  console.log("Connected to WebSocket");
};

// Handle messages
ws.onmessage = function (event) {
  const data = JSON.parse(event.data);
  console.log("Received:", data);
};

// Send message
ws.send(
  JSON.stringify({
    type: "event_update",
    message: "Hello, GatherHub!",
  })
);
```

### Real-time Events

- **Event Updates**: Live event changes and notifications
- **Task Updates**: Real-time task assignments and completions
- **Vote Updates**: Live voting results and new votes
- **User Status**: Online/offline status and activity

### WebSocket Endpoints

- `/ws/events/` - Event-related updates
- `/ws/tasks/` - Task-related updates
- `/ws/voting/` - Voting-related updates

## 🔐 Authentication Flow

### Registration and Login

1. **Register**: `POST /api/v1/auth/register/`

   ```json
   {
     "username": "newuser",
     "email": "user@example.com",
     "password": "securepassword",
     "first_name": "John",
     "last_name": "Doe"
   }
   ```

2. **Login**: `POST /api/v1/auth/login/`

   ```json
   {
     "username": "newuser",
     "password": "securepassword"
   }
   ```

3. **Response**:
   ```json
   {
     "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
     "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
     "user": {
       "id": 1,
       "username": "newuser",
       "email": "user@example.com"
     }
   }
   ```

### Using JWT Tokens

```javascript
// Include in API requests
fetch("/api/v1/events/", {
  headers: {
    Authorization: "Bearer " + accessToken,
    "Content-Type": "application/json",
  },
});

// Refresh token when expired
const refreshResponse = await fetch("/api/v1/auth/refresh/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ refresh: refreshToken }),
});
```

## 📊 Rate Limiting

### API Rate Limits

- **Authentication endpoints**: 5 requests/minute
- **General API endpoints**: 100 requests/minute
- **File uploads**: 10 requests/minute

### Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Error Response

```json
{
  "error": "Rate limit exceeded",
  "detail": "Expected available in 60 seconds."
}
```

## 🚀 Production Deployment

### Environment Variables

```bash
# Core Django Settings
SECRET_KEY=your-super-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Redis
REDIS_URL=redis://host:port/0

# CORS
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com

# Security
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

### Render.com Deployment

#### 1. Automatic Deployment

The repository includes `render.yaml` for automatic deployment:

```bash
# Push to GitHub
git push origin main

# Deploy will trigger automatically on Render
```

#### 2. Manual Setup

1. **Create Web Service** on Render
2. **Connect GitHub Repository**
3. **Configure Build Command**:
   ```bash
   pip install -r requirements.prod.txt && python manage.py collectstatic --noinput && python manage.py migrate
   ```
4. **Configure Start Command**:
   ```bash
   gunicorn --bind 0.0.0.0:$PORT --workers 3 --worker-class uvicorn.workers.UvicornWorker gatherhub.asgi:application
   ```

#### 3. Add Required Services

- **PostgreSQL Database**: Add PostgreSQL service
- **Redis Cache**: Add Redis service
- **Environment Variables**: Configure in Render dashboard

### Docker Production Deployment

```bash
# Build production image
docker build -t gatherhub:latest .

# Run with production settings
docker-compose -f docker-compose.prod.yml up -d
```

## 🏥 Health Monitoring

### Health Check Endpoints

- `/health/` - Basic health check
- `/health/ready/` - Readiness check (all services)
- `/health/live/` - Liveness check
- `/health/status/` - Detailed status dashboard

### Health Check Response

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "checks": {
    "database": { "status": "healthy", "latency_ms": 5.2 },
    "redis": { "status": "healthy", "latency_ms": 1.1 },
    "channels": { "status": "healthy", "latency_ms": 2.3 }
  }
}
```

### Monitoring Script

```bash
# Run health check script
./scripts/health_check.sh

# Check specific endpoint
curl -f http://localhost:8000/health/ready/
```

## 🛠️ Development

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .

# Security check
bandit -r .
```

### Database Management

```bash
# Create migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database
python manage.py flush

# Create test data
python manage.py loaddata fixtures/sample_data.json
```

### Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.events

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 🔧 Configuration

### Settings Files

- `gatherhub/settings/base.py` - Base settings
- `gatherhub/settings/development.py` - Development settings
- `gatherhub/settings/production.py` - Production settings
- `gatherhub/settings/render.py` - Render.com specific settings

### Environment Variables

```bash
# Django
DJANGO_SETTINGS_MODULE=gatherhub.settings.production
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Cache
REDIS_URL=redis://host:port/db

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-password
```

## 🔐 Security

### Security Features

- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: API endpoint protection
- **CORS Configuration**: Cross-origin request control
- **CSRF Protection**: Cross-site request forgery protection
- **SQL Injection Protection**: Django ORM protection
- **XSS Protection**: Cross-site scripting prevention
- **HTTPS Enforcement**: Secure connection requirements

### Security Headers

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

## 📝 Error Handling

### Error Response Format

```json
{
  "error": "error_code",
  "message": "Human readable error message",
  "details": {
    "field": ["Field specific error"]
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Common Error Codes

- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Rate Limited
- `500` - Internal Server Error

## 🤝 Frontend Integration

### Getting Started

1. **Set up CORS**: Configure `CORS_ALLOWED_ORIGINS` for your frontend domain
2. **Authentication**: Implement JWT token handling
3. **WebSocket**: Connect to real-time updates
4. **Error Handling**: Handle API errors appropriately

### Example React Integration

```javascript
// API Client setup
const apiClient = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("accessToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle token refresh or redirect to login
    }
    return Promise.reject(error);
  }
);
```

### WebSocket Integration

```javascript
// WebSocket connection
const wsUrl = "ws://localhost:8000/ws/events/";
const socket = new WebSocket(wsUrl);

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle real-time updates
  updateUI(data);
};
```

## 📖 API Examples

### Create an Event

```bash
curl -X POST http://localhost:8000/api/v1/events/ \\
  -H "Authorization: Bearer <token>" \\
  -H "Content-Type: application/json" \\
  -d '{
    "title": "Community Meetup",
    "description": "Monthly community gathering",
    "date": "2024-02-15T18:00:00Z",
    "location": "Community Center",
    "max_participants": 50
  }'
```

### Join an Event

```bash
curl -X POST http://localhost:8000/api/v1/events/1/join/ \\
  -H "Authorization: Bearer <token>"
```

### Create a Vote

```bash
curl -X POST http://localhost:8000/api/v1/voting/ \\
  -H "Authorization: Bearer <token>" \\
  -H "Content-Type: application/json" \\
  -d '{
    "title": "Choose the venue",
    "description": "Where should we hold the next meetup?",
    "event": 1,
    "options": [
      {"text": "Community Center"},
      {"text": "Public Library"},
      {"text": "Park Pavilion"}
    ],
    "ends_at": "2024-02-10T23:59:59Z"
  }'
```

## 📚 Additional Resources

### Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Channels](https://channels.readthedocs.io/)
- [Render.com Documentation](https://render.com/docs)

### Community

- [GitHub Issues](https://github.com/JeanEudes-dev/GatherHub/issues)
- [Discussions](https://github.com/JeanEudes-dev/GatherHub/discussions)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django and Django REST Framework communities
- Contributors and testers
- Open source libraries and tools used

---

**GatherHub Backend** - Bringing communities together through technology 🌟

For questions or support, please open an issue on [GitHub](https://github.com/JeanEudes-dev/GatherHub/issues) or contact the development team.

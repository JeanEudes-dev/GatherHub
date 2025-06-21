# GatherHub - Django Backend Project

## Overview

GatherHub is a real-time community event planner built with Django 5+ and Django REST Framework. This project provides a solid foundation for building collaborative event planning features with real-time capabilities.

## Project Structure

```
gatherhub/
├── manage.py
├── requirements.txt
├── .env.example
├── gatherhub/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── __init__.py
│   ├── accounts/       # User management
│   ├── events/         # Event management
│   ├── voting/         # Time slot voting
│   └── tasks/          # Task management
├── static/
├── media/
├── logs/
└── venv/
```

## Core Models

### 1. CustomUser (accounts.models.CustomUser)

- **Purpose**: Extended user model with email as username
- **Fields**:
  - `email` (EmailField, unique) - Primary identifier
  - `name` (CharField) - Display name
  - `avatar` (ImageField, optional) - Profile picture
  - Inherits all fields from AbstractUser

### 2. Event (events.models.Event)

- **Purpose**: Represents a community event
- **Fields**:
  - `title` (CharField) - Event name
  - `description` (TextField) - Event description
  - `slug` (SlugField, unique) - URL-friendly identifier
  - `status` (CharField) - 'draft' or 'locked'
  - `created_by` (ForeignKey to CustomUser) - Event organizer
  - `created_at`, `updated_at` - Timestamps

### 3. TimeSlot (events.models.TimeSlot)

- **Purpose**: Represents potential meeting times for events
- **Fields**:
  - `event` (ForeignKey to Event) - Associated event
  - `datetime` (DateTimeField) - Proposed time
  - `created_at` - Timestamp
- **Constraints**: Unique together (event, datetime)

### 4. Vote (voting.models.Vote)

- **Purpose**: Tracks user votes for time slots
- **Fields**:
  - `user` (ForeignKey to CustomUser) - Voting user
  - `timeslot` (ForeignKey to TimeSlot) - Voted time slot
  - `created_at` - Timestamp
- **Constraints**: Unique together (user, timeslot)

### 5. Task (tasks.models.Task)

- **Purpose**: Event-related tasks and assignments
- **Fields**:
  - `event` (ForeignKey to Event) - Associated event
  - `title` (CharField) - Task description
  - `status` (CharField) - 'todo', 'doing', or 'done'
  - `assigned_to` (ForeignKey to CustomUser, nullable) - Assignee
  - `created_at`, `updated_at` - Timestamps

## Technology Stack

### Core Framework

- **Django 5.0+**: Web framework
- **Django REST Framework**: API development
- **PostgreSQL**: Primary database (SQLite fallback for development)

### Real-time Features

- **Django Channels**: WebSocket support
- **Redis**: Channel layer backend

### Authentication

- **Django REST Framework SimpleJWT**: Token-based authentication
- **Custom User Model**: Email-based authentication

### Additional Features

- **django-cors-headers**: Cross-Origin Resource Sharing
- **drf-spectacular**: API documentation
- **Pillow**: Image handling
- **python-decouple**: Environment variable management

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_NAME=gatherhub_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Redis (for Channels)
REDIS_URL=redis://localhost:6379/0
```

### Settings Structure

- **base.py**: Common settings for all environments
- **development.py**: Development-specific settings (SQLite, debug toolbar)
- **production.py**: Production settings (PostgreSQL, security headers)

## Admin Interface

All models are registered in Django admin with comprehensive interfaces:

- **Users**: Managed through CustomUserAdmin with additional fields
- **Events**: Full event management with slug auto-generation
- **Time Slots**: Time slot management with event filtering
- **Votes**: Vote tracking with user and event filtering
- **Tasks**: Task management with status tracking

## API Endpoints

### Authentication (`/api/v1/auth/`)

- `POST /token/` - Obtain JWT token
- `POST /token/refresh/` - Refresh JWT token
- `POST /token/verify/` - Verify JWT token

### Future Endpoints

- `/api/v1/events/` - Event management
- `/api/v1/voting/` - Voting functionality
- `/api/v1/tasks/` - Task management

## Installation & Setup

1. **Create Virtual Environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Database Setup**:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run Development Server**:
   ```bash
   python manage.py runserver
   ```

## Security Features

### Development

- Debug toolbar for development
- CORS enabled for local development
- Console email backend

### Production

- SSL redirect enforced
- HSTS headers configured
- Secure cookie settings
- CSRF protection
- XSS protection

## Logging

- Console logging for development
- File logging for production
- Separate loggers for Django and GatherHub components

## Next Steps

1. **API Development**: Implement REST API endpoints for all models
2. **WebSocket Integration**: Add real-time features for voting and task updates
3. **User Registration**: Implement user registration and profile management
4. **Event Workflows**: Add event creation, invitation, and management flows
5. **Notification System**: Implement email and real-time notifications
6. **Frontend Integration**: Connect with React/Vue.js frontend
7. **Testing**: Add comprehensive test coverage
8. **Documentation**: Generate API documentation with Swagger/OpenAPI

## Development Notes

- Custom user model is configured and ready
- All migrations are created and applied
- Admin interface is fully configured
- JWT authentication is set up
- Real-time infrastructure (Channels) is configured
- Project follows Django best practices
- Code is organized in reusable apps
- Settings are split for different environments

The project is now ready for feature development and can be extended with additional functionality as needed.

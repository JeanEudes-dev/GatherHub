# Contributing to GatherHub

We love your input! We want to make contributing to GatherHub as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## We Develop with GitHub

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## We Use [GitHub Flow](https://guides.github.com/introduction/flow/index.html)

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project.

## Report bugs using GitHub's [issues](https://github.com/JeanEudes-dev/GatherHub/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/JeanEudes-dev/GatherHub/issues/new).

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Development Environment Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Git

### Setup Steps

1. **Clone your fork**

   ```bash
   git clone https://github.com/YOUR_USERNAME/GatherHub.git
   cd GatherHub
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## Code Style

We use several tools to maintain code quality:

### Python Code Style

- **Black** for code formatting
- **flake8** for linting
- **isort** for import sorting

```bash
# Format code
black .

# Check linting
flake8 .

# Sort imports
isort .
```

### Pre-commit Hooks

We recommend setting up pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

## Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.events

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Writing Tests

- Write tests for all new functionality
- Maintain or improve test coverage
- Use Django's TestCase for database-dependent tests
- Use SimpleTestCase for non-database tests

### Test Structure

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.events.models import Event

User = get_user_model()

class EventModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_event_creation(self):
        event = Event.objects.create(
            title='Test Event',
            creator=self.user,
            # ... other fields
        )
        self.assertEqual(event.title, 'Test Event')
        self.assertEqual(event.creator, self.user)
```

## API Documentation

When adding new API endpoints:

1. **Add docstrings** to your views
2. **Update OpenAPI schema** if needed
3. **Add examples** in docstrings
4. **Update README.md** with new endpoints

### API Documentation Example

```python
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.response import Response

class EventViewSet(ModelViewSet):
    @extend_schema(
        summary="Create a new event",
        description="Create a new event with the provided details.",
        responses={
            201: OpenApiResponse(description="Event created successfully"),
            400: OpenApiResponse(description="Invalid input data"),
        }
    )
    def create(self, request):
        # Implementation
        pass
```

## Database Migrations

### Creating Migrations

```bash
# Create migrations for all apps
python manage.py makemigrations

# Create migration for specific app
python manage.py makemigrations events
```

### Migration Best Practices

- Always review migrations before committing
- Use descriptive migration names
- Test migrations on a copy of production data
- Consider backward compatibility

## Git Workflow

### Branching Strategy

- `main` - production-ready code
- `develop` - integration branch for features
- `feature/description` - feature branches
- `bugfix/description` - bug fix branches
- `hotfix/description` - urgent production fixes

### Commit Messages

Use clear and descriptive commit messages:

```
feat: add user authentication endpoints
fix: resolve vote counting bug
docs: update API documentation
test: add tests for event creation
refactor: improve database query performance
```

### Pull Request Process

1. **Create a feature branch**

   ```bash
   git checkout -b feature/new-feature
   ```

2. **Make your changes**

   - Write code
   - Add tests
   - Update documentation

3. **Test your changes**

   ```bash
   python manage.py test
   flake8 .
   black --check .
   ```

4. **Commit and push**

   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin feature/new-feature
   ```

5. **Create pull request**
   - Use the GitHub interface
   - Fill out the PR template
   - Request review from maintainers

## Security

### Reporting Security Vulnerabilities

Please report security vulnerabilities to [security@gatherhub.com](mailto:security@gatherhub.com) instead of using the public issue tracker.

### Security Best Practices

- Never commit secrets or credentials
- Use environment variables for configuration
- Follow Django security guidelines
- Keep dependencies updated

## Performance

### Performance Guidelines

- Use database indexes appropriately
- Optimize queries (use `select_related` and `prefetch_related`)
- Implement caching where appropriate
- Monitor API response times

### Database Optimization

```python
# Good: Use select_related for foreign keys
events = Event.objects.select_related('creator').all()

# Good: Use prefetch_related for many-to-many
events = Event.objects.prefetch_related('participants').all()

# Bad: N+1 queries
for event in Event.objects.all():
    print(event.creator.username)  # Triggers additional query
```

## Documentation

### Updating Documentation

- Update README.md for significant changes
- Update API documentation for new endpoints
- Add inline code comments for complex logic
- Update configuration documentation for new settings

### Documentation Standards

- Use clear, concise language
- Include code examples
- Keep documentation up-to-date
- Use proper markdown formatting

## Getting Help

### Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [GitHub Discussions](https://github.com/JeanEudes-dev/GatherHub/discussions)

### Contact

- Create an issue for bugs or feature requests
- Use GitHub Discussions for questions
- Join our community chat (link in README)

## Recognition

Contributors will be recognized in the following ways:

- Listed in the project's contributors
- Mentioned in release notes for significant contributions
- Invited to join the maintainer team for sustained contributions

Thank you for contributing to GatherHub! 🎉

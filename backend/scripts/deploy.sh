#!/bin/bash

# GatherHub Deployment Script for Render.com
# This script handles the deployment process

set -e  # Exit on any error

echo "🚀 Starting GatherHub deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in a production environment
if [ "$DJANGO_SETTINGS_MODULE" != "gatherhub.settings.render" ] && [ "$DJANGO_SETTINGS_MODULE" != "gatherhub.settings.production" ]; then
    print_warning "DJANGO_SETTINGS_MODULE is not set to production settings"
    print_warning "Current value: $DJANGO_SETTINGS_MODULE"
fi

# Check required environment variables
required_vars=("SECRET_KEY" "DATABASE_URL" "REDIS_URL")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        print_error "Required environment variable $var is not set"
        exit 1
    fi
done

print_status "Environment variables validated"

# Install dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.prod.txt

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run database migrations
print_status "Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist (optional)
if [ "$CREATE_SUPERUSER" = "true" ]; then
    print_status "Creating superuser..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@gatherhub.com', '$(echo $ADMIN_PASSWORD)')
    print('Superuser created')
else:
    print('Superuser already exists')
"
fi

# Validate deployment
print_status "Validating deployment..."
python manage.py check --deploy

# Test database connection
print_status "Testing database connection..."
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT 1')
print('Database connection successful')
"

# Test Redis connection
print_status "Testing Redis connection..."
python manage.py shell -c "
from django.core.cache import cache
cache.set('deployment_test', 'success', 30)
result = cache.get('deployment_test')
if result == 'success':
    print('Redis connection successful')
else:
    raise Exception('Redis connection failed')
"

print_status "✅ Deployment completed successfully!"
print_status "Application is ready to start"

# Optional: Run health check
if command -v curl &> /dev/null; then
    print_status "Running health check..."
    # Wait a moment for the server to start if this is called during startup
    sleep 5
    if curl -f http://localhost:${PORT:-8000}/health/ &> /dev/null; then
        print_status "✅ Health check passed"
    else
        print_warning "Health check endpoint not yet available (this is normal during initial deployment)"
    fi
fi

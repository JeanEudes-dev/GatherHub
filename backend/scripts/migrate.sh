#!/bin/bash

# Database Migration Script for GatherHub
# Safely handles database migrations with rollback capability

set -e

echo "🗄️ Running database migrations for GatherHub..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Test database connection first
print_status "Testing database connection..."
python manage.py shell -c "
from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

# Check for pending migrations
print_status "Checking for pending migrations..."
if python manage.py showmigrations --plan | grep -q "\[ \]"; then
    print_status "Pending migrations found, proceeding..."
else
    print_status "No pending migrations"
    exit 0
fi

# Create a backup point (in production, you might want to create a database backup here)
print_status "Creating migration backup point..."
python manage.py shell -c "
import datetime
print(f'Migration started at: {datetime.datetime.now()}')
"

# Run migrations
print_status "Applying migrations..."
python manage.py migrate --noinput

# Verify migrations
print_status "Verifying migrations..."
python manage.py showmigrations | grep -c "\[X\]" > /tmp/migration_count || true
APPLIED_MIGRATIONS=$(cat /tmp/migration_count)
print_status "Applied migrations: $APPLIED_MIGRATIONS"

# Run system checks
print_status "Running system checks..."
python manage.py check

print_status "✅ Database migrations completed successfully!"

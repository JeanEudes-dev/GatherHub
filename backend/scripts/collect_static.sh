#!/bin/bash

# Static Files Collection Script for GatherHub
# Handles static file collection with optimization

set -e

echo "📁 Collecting static files for GatherHub..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if static directory exists and create if not
if [ ! -d "static" ]; then
    print_status "Creating static directory..."
    mkdir -p static
fi

# Clear existing static files
print_status "Clearing existing static files..."
if [ -d "static" ]; then
    find static -type f -name "*.css" -o -name "*.js" -o -name "*.png" -o -name "*.jpg" -o -name "*.gif" -o -name "*.svg" | wc -l > /tmp/old_files_count
    OLD_FILES=$(cat /tmp/old_files_count)
    print_status "Found $OLD_FILES existing static files"
fi

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Count collected files
if [ -d "static" ]; then
    find static -type f | wc -l > /tmp/new_files_count
    NEW_FILES=$(cat /tmp/new_files_count)
    print_status "Collected $NEW_FILES static files"
fi

# Check for common static files
check_file() {
    if [ -f "$1" ]; then
        print_status "✅ Found: $1"
    else
        print_warning "❌ Missing: $1"
    fi
}

print_status "Verifying critical static files..."
check_file "static/admin/css/base.css"
check_file "static/admin/js/core.js"
check_file "static/rest_framework/css/bootstrap.min.css"

# Check static files size
if [ -d "static" ]; then
    STATIC_SIZE=$(du -sh static | cut -f1)
    print_status "Total static files size: $STATIC_SIZE"
fi

print_status "✅ Static files collection completed successfully!"

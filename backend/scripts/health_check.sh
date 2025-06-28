#!/bin/bash

# Health Check Script for GatherHub
# Comprehensive health monitoring for production deployment

set -e

# Configuration
HOST=${HOST:-localhost}
PORT=${PORT:-8000}
PROTOCOL=${PROTOCOL:-http}
BASE_URL="${PROTOCOL}://${HOST}:${PORT}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ]${NC} $1"
}

# Function to make HTTP requests with timeout
make_request() {
    local url=$1
    local expected_status=${2:-200}
    local timeout=${3:-10}
    
    if command -v curl &> /dev/null; then
        response=$(curl -s -w "\n%{http_code}" --max-time $timeout "$url" 2>/dev/null || echo -e "\n000")
        status_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | head -n -1)
    else
        print_error "curl is not available"
        return 1
    fi
    
    if [ "$status_code" = "$expected_status" ]; then
        return 0
    else
        return 1
    fi
}

echo "🏥 GatherHub Health Check"
echo "========================"
print_info "Checking health of: $BASE_URL"
echo

# Track overall health
OVERALL_HEALTH=0

# Basic health check
print_info "1. Basic Health Check"
if make_request "$BASE_URL/health/"; then
    print_status "Basic health check passed"
else
    print_error "Basic health check failed (Status: $status_code)"
    OVERALL_HEALTH=1
fi
echo

# Readiness check
print_info "2. Readiness Check"
if make_request "$BASE_URL/health/ready/"; then
    print_status "Readiness check passed"
    # Parse JSON response if possible
    if command -v python3 &> /dev/null; then
        echo "$body" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"  Status: {data.get('status', 'unknown')}\")
    if 'checks' in data:
        for service, check in data['checks'].items():
            status = check.get('status', 'unknown')
            latency = check.get('latency_ms', 'N/A')
            if status == 'healthy':
                print(f\"  ✓ {service}: {status} ({latency}ms)\")
            else:
                print(f\"  ✗ {service}: {status}\")
except:
    pass
" 2>/dev/null || true
    fi
else
    print_error "Readiness check failed (Status: $status_code)"
    OVERALL_HEALTH=1
fi
echo

# Liveness check
print_info "3. Liveness Check"
if make_request "$BASE_URL/health/live/"; then
    print_status "Liveness check passed"
else
    print_error "Liveness check failed (Status: $status_code)"
    OVERALL_HEALTH=1
fi
echo

# API endpoints check
print_info "4. API Endpoints Check"
API_ENDPOINTS=(
    "/api/v1/auth/register/"
    "/api/v1/events/"
    "/api/v1/tasks/"
    "/api/v1/voting/"
)

for endpoint in "${API_ENDPOINTS[@]}"; do
    # For API endpoints, 401 (Unauthorized) is acceptable as it means the endpoint exists
    if make_request "$BASE_URL$endpoint" 200 5 || make_request "$BASE_URL$endpoint" 401 5; then
        print_status "API endpoint $endpoint is accessible"
    else
        print_warning "API endpoint $endpoint may not be accessible (Status: $status_code)"
    fi
done
echo

# Database connectivity (via health check)
print_info "5. Database Connectivity"
if make_request "$BASE_URL/health/ready/" && echo "$body" | grep -q '"database".*"healthy"'; then
    print_status "Database connectivity confirmed"
else
    print_error "Database connectivity issues detected"
    OVERALL_HEALTH=1
fi

# Redis connectivity (via health check)
print_info "6. Redis Connectivity"
if make_request "$BASE_URL/health/ready/" && echo "$body" | grep -q '"redis".*"healthy"'; then
    print_status "Redis connectivity confirmed"
else
    print_warning "Redis connectivity issues detected"
fi

# WebSocket connectivity (basic check)
print_info "7. WebSocket Support"
if make_request "$BASE_URL/health/ready/" && echo "$body" | grep -q '"channels".*"healthy"'; then
    print_status "WebSocket support confirmed"
else
    print_warning "WebSocket support issues detected"
fi

echo
echo "========================"
if [ $OVERALL_HEALTH -eq 0 ]; then
    print_status "🎉 Overall Health: HEALTHY"
    echo
    print_info "All critical systems are operational"
    exit 0
else
    print_error "💔 Overall Health: UNHEALTHY"
    echo
    print_error "Critical issues detected - check the logs above"
    exit 1
fi

"""
GatherHub Custom Middleware

Security, rate limiting, and API enhancement middleware.
"""
import logging
import time
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger('gatherhub.security')


class APISecurityMiddleware:
    """
    Add comprehensive security headers to API responses.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Only apply to API requests
        if request.path.startswith('/api/'):
            # Security headers
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            response['X-Permitted-Cross-Domain-Policies'] = 'none'
            
            # API-specific headers
            response['X-API-Version'] = '1.0'
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            
            # Remove server information
            if 'Server' in response:
                del response['Server']
        
        return response


class APIRateLimitMiddleware:
    """
    Rate limiting middleware for API endpoints with different limits per endpoint type.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limits = {
            # Format: (requests, time_window_seconds)
            'auth': (5, 60),      # 5 requests per minute for auth
            'voting': (10, 60),   # 10 votes per minute
            'tasks': (20, 60),    # 20 task updates per minute
            'general': (100, 60), # 100 general API requests per minute
        }

    def __call__(self, request):
        # Only apply rate limiting to API requests
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        # Skip rate limiting for superusers in development
        if settings.DEBUG and hasattr(request, 'user') and request.user.is_authenticated and request.user.is_superuser:
            return self.get_response(request)
        
        # Determine rate limit type based on URL
        limit_type = self._get_limit_type(request.path)
        
        # Check rate limit
        if not self._check_rate_limit(request, limit_type):
            logger.warning(f"Rate limit exceeded for {request.user} on {request.path}")
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'detail': f'Too many requests. Please try again later.',
                'type': limit_type
            }, status=429)
        
        response = self.get_response(request)
        
        # Add rate limit headers
        self._add_rate_limit_headers(response, request, limit_type)
        
        return response
    
    def _get_limit_type(self, path):
        """Determine the type of rate limit based on the URL path."""
        if any(auth_path in path for auth_path in ['/auth/', '/login/', '/register/', '/token/']):
            return 'auth'
        elif '/voting/' in path or '/vote/' in path:
            return 'voting'
        elif '/tasks/' in path:
            return 'tasks'
        else:
            return 'general'
    
    def _check_rate_limit(self, request, limit_type):
        """Check if the request is within rate limits."""
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Get rate limit settings
        max_requests, time_window = self.rate_limits.get(limit_type, self.rate_limits['general'])
        
        # Create cache key
        cache_key = f"rate_limit:{limit_type}:{client_id}"
        
        # Get current request count
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= max_requests:
            return False
        
        # Increment counter
        cache.set(cache_key, current_requests + 1, time_window)
        
        return True
    
    def _get_client_id(self, request):
        """Get a unique identifier for the client."""
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"user:{request.user.id}"
        else:
            # Use IP address for anonymous users
            ip = self._get_client_ip(request)
            return f"ip:{ip}"
    
    def _get_client_ip(self, request):
        """Get the client's IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _add_rate_limit_headers(self, response, request, limit_type):
        """Add rate limit information to response headers."""
        client_id = self._get_client_id(request)
        cache_key = f"rate_limit:{limit_type}:{client_id}"
        max_requests, time_window = self.rate_limits.get(limit_type, self.rate_limits['general'])
        current_requests = cache.get(cache_key, 0)
        
        response['X-RateLimit-Limit'] = str(max_requests)
        response['X-RateLimit-Remaining'] = str(max(0, max_requests - current_requests))
        response['X-RateLimit-Reset'] = str(int(time.time()) + time_window)
        response['X-RateLimit-Type'] = limit_type


class APIVersioningMiddleware:
    """
    Handle API versioning and deprecation warnings.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.current_version = '1.0'
        self.supported_versions = ['1.0']

    def __call__(self, request):
        # Only apply to API requests
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        # Get requested API version
        api_version = request.META.get('HTTP_API_VERSION', self.current_version)
        
        # Validate version
        if api_version not in self.supported_versions:
            return JsonResponse({
                'error': 'Unsupported API version',
                'detail': f'API version {api_version} is not supported. Supported versions: {", ".join(self.supported_versions)}',
                'supported_versions': self.supported_versions
            }, status=400)
        
        # Store version in request for use in views
        request.api_version = api_version
        
        response = self.get_response(request)
        
        # Add version headers
        response['X-API-Version'] = self.current_version
        response['X-Supported-Versions'] = ', '.join(self.supported_versions)
        
        return response


class SecurityLoggingMiddleware:
    """
    Log security-related events and suspicious activities.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.security_logger = logging.getLogger('django.security')

    def __call__(self, request):
        start_time = time.time()
        
        # Log API access
        if request.path.startswith('/api/'):
            self._log_api_access(request)
        
        response = self.get_response(request)
        
        # Log security events
        self._log_security_events(request, response, start_time)
        
        return response
    
    def _log_api_access(self, request):
        """Log API access attempts."""
        user_info = 'anonymous'
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_info = f"{request.user.email} (ID: {request.user.id})"
        
        self.security_logger.info(
            f"API Access: {request.method} {request.path} by {user_info} "
            f"from {self._get_client_ip(request)}"
        )
    
    def _log_security_events(self, request, response, start_time):
        """Log security-related events."""
        # Log failed authentication attempts
        if response.status_code == 401:
            self.security_logger.warning(
                f"Authentication failed: {request.method} {request.path} "
                f"from {self._get_client_ip(request)}"
            )
        
        # Log permission denied attempts
        elif response.status_code == 403:
            user_info = 'anonymous'
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_info = f"{request.user.email} (ID: {request.user.id})"
            
            self.security_logger.warning(
                f"Permission denied: {request.method} {request.path} by {user_info} "
                f"from {self._get_client_ip(request)}"
            )
        
        # Log rate limit violations
        elif response.status_code == 429:
            self.security_logger.warning(
                f"Rate limit exceeded: {request.method} {request.path} "
                f"from {self._get_client_ip(request)}"
            )
        
        # Log slow requests (potential DoS)
        request_time = time.time() - start_time
        if request_time > 5.0:  # Requests taking more than 5 seconds
            self.security_logger.warning(
                f"Slow request detected: {request.method} {request.path} "
                f"took {request_time:.2f}s from {self._get_client_ip(request)}"
            )
    
    def _get_client_ip(self, request):
        """Get the client's IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class InputValidationMiddleware:
    """
    Additional input validation and sanitization middleware.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        self.suspicious_patterns = [
            'script>', '<iframe', 'javascript:', 'vbscript:', 'onload=', 'onerror=',
            'UNION SELECT', 'DROP TABLE', 'INSERT INTO', 'DELETE FROM'
        ]

    def __call__(self, request):
        # Only apply to API requests
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        # Check request size
        if hasattr(request, 'META') and 'CONTENT_LENGTH' in request.META:
            try:
                content_length = int(request.META['CONTENT_LENGTH'])
                if content_length > self.max_request_size:
                    logger.warning(f"Large request blocked: {content_length} bytes from {self._get_client_ip(request)}")
                    return JsonResponse({
                        'error': 'Request too large',
                        'detail': 'Request size exceeds maximum allowed limit'
                    }, status=413)
            except (ValueError, TypeError):
                pass
        
        # Basic input validation for suspicious patterns
        if request.method in ['POST', 'PUT', 'PATCH']:
            if self._contains_suspicious_content(request):
                logger.warning(f"Suspicious content detected in request from {self._get_client_ip(request)}")
                return JsonResponse({
                    'error': 'Invalid input',
                    'detail': 'Request contains potentially malicious content'
                }, status=400)
        
        return self.get_response(request)
    
    def _contains_suspicious_content(self, request):
        """Check if request contains suspicious patterns."""
        try:
            # Check query parameters
            for key, value in request.GET.items():
                if any(pattern.lower() in str(value).lower() for pattern in self.suspicious_patterns):
                    return True
            
            # Check POST data if available
            if hasattr(request, 'body') and request.body:
                body_str = request.body.decode('utf-8', errors='ignore').lower()
                if any(pattern.lower() in body_str for pattern in self.suspicious_patterns):
                    return True
        except (UnicodeDecodeError, AttributeError):
            # If we can't decode the request, let it through but log it
            logger.info(f"Could not decode request body from {self._get_client_ip(request)}")
        
        return False
    
    def _get_client_ip(self, request):
        """Get the client's IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

import time
import redis
from django.db import connection
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from channels.layers import get_channel_layer


@never_cache
@require_http_methods(["GET"])
def health_check(request):
    """Basic health check endpoint."""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })


@never_cache
@require_http_methods(["GET"])
def ready_check(request):
    """Readiness check - all services must be available."""
    start_time = time.time()
    checks = {}
    overall_status = 'healthy'
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            checks['database'] = {
                'status': 'healthy',
                'latency_ms': round((time.time() - start_time) * 1000, 2)
            }
    except Exception as e:
        checks['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        overall_status = 'unhealthy'
    
    # Redis check
    try:
        redis_start = time.time()
        if hasattr(settings, 'CACHES') and 'default' in settings.CACHES:
            # Try to connect to Redis
            from django.core.cache import cache
            cache.set('health_check', 'ok', 30)
            result = cache.get('health_check')
            if result == 'ok':
                checks['redis'] = {
                    'status': 'healthy',
                    'latency_ms': round((time.time() - redis_start) * 1000, 2)
                }
            else:
                checks['redis'] = {
                    'status': 'unhealthy',
                    'error': 'Cache write/read failed'
                }
                overall_status = 'unhealthy'
        else:
            checks['redis'] = {
                'status': 'not_configured'
            }
    except Exception as e:
        checks['redis'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        overall_status = 'unhealthy'
    
    # Channels layer check (WebSocket support)
    try:
        channels_start = time.time()
        channel_layer = get_channel_layer()
        if channel_layer:
            # Try to send a test message
            from asgiref.sync import async_to_sync
            test_channel = 'health-check-' + str(int(time.time()))
            async_to_sync(channel_layer.send)(test_channel, {
                'type': 'test.message',
                'data': 'health_check'
            })
            checks['channels'] = {
                'status': 'healthy',
                'latency_ms': round((time.time() - channels_start) * 1000, 2)
            }
        else:
            checks['channels'] = {
                'status': 'not_configured'
            }
    except Exception as e:
        checks['channels'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        overall_status = 'unhealthy'
    
    response_data = {
        'status': overall_status,
        'timestamp': timezone.now().isoformat(),
        'checks': checks,
        'total_latency_ms': round((time.time() - start_time) * 1000, 2)
    }
    
    status_code = 200 if overall_status == 'healthy' else 503
    return JsonResponse(response_data, status=status_code)


@never_cache
@require_http_methods(["GET"])
def live_check(request):
    """Liveness check - basic application availability."""
    try:
        # Basic Django functionality check
        from django.apps import apps
        apps.check_apps_ready()
        
        return JsonResponse({
            'status': 'alive',
            'timestamp': timezone.now().isoformat(),
            'django_ready': True
        })
    except Exception as e:
        return JsonResponse({
            'status': 'dead',
            'timestamp': timezone.now().isoformat(),
            'error': str(e)
        }, status=503)


@never_cache
@require_http_methods(["GET"])
def status_dashboard(request):
    """Comprehensive status dashboard."""
    start_time = time.time()
    
    # Get system info
    import platform
    import sys
    import os
    
    system_info = {
        'python_version': sys.version,
        'platform': platform.platform(),
        'django_version': __import__('django').get_version(),
        'process_id': os.getpid(),
        'environment': getattr(settings, 'ENVIRONMENT', 'unknown')
    }
    
    # Get database info
    db_info = {}
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            db_result = cursor.fetchone()
            db_version = db_result[0] if db_result else 'unknown'
            
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
            table_result = cursor.fetchone()
            table_count = table_result[0] if table_result else 0
            
            db_info = {
                'status': 'connected',
                'version': db_version,
                'table_count': table_count,
                'connection_max_age': getattr(settings, 'DATABASES', {}).get('default', {}).get('CONN_MAX_AGE', 0)
            }
    except Exception as e:
        db_info = {
            'status': 'error',
            'error': str(e)
        }
    
    # Get cache info
    cache_info = {}
    try:
        from django.core.cache import cache
        cache.set('status_check', 'working', 30)
        if cache.get('status_check') == 'working':
            cache_info = {
                'status': 'working',
                'backend': settings.CACHES.get('default', {}).get('BACKEND', 'unknown')
            }
        else:
            cache_info = {
                'status': 'error',
                'error': 'Cache read/write failed'
            }
    except Exception as e:
        cache_info = {
            'status': 'error',
            'error': str(e)
        }
    
    return JsonResponse({
        'status': 'ok',
        'timestamp': timezone.now().isoformat(),
        'uptime_check_ms': round((time.time() - start_time) * 1000, 2),
        'system': system_info,
        'database': db_info,
        'cache': cache_info,
        'debug_mode': settings.DEBUG,
        'allowed_hosts': settings.ALLOWED_HOSTS
    })

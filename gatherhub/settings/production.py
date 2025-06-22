"""
Production settings for GatherHub project.
Enhanced security configuration for production deployment.
"""

from .base import *

# Production security settings
DEBUG = False

# Enhanced allowed hosts for production
ALLOWED_HOSTS = [
    'gatherhub.com',
    'www.gatherhub.com',
    'api.gatherhub.com',
    '.gatherhub.com',  # Allow all subdomains
]

# Production database settings (PostgreSQL required)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST', default='localhost'),
        'PORT': config('DATABASE_PORT', default='5432'),
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Enhanced Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Enhanced Session security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Enhanced CSRF security
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_TRUSTED_ORIGINS = [
    'https://gatherhub.com',
    'https://www.gatherhub.com',
    'https://api.gatherhub.com',
]

# Production CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://gatherhub.com",
    "https://www.gatherhub.com",
    "https://app.gatherhub.com",
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.gatherhub\.com$",
]

# Enhanced CSP for production
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ("'self'",),
        'script-src': ("'self'", "https://cdn.jsdelivr.net", "https://unpkg.com"),
        'style-src': ("'self'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net"),
        'img-src': ("'self'", "data:", "https:", "blob:"),
        'connect-src': ("'self'", "wss:", "https:"),
        'font-src': ("'self'", "https://fonts.gstatic.com"),
        'object-src': ("'none'",),
        'base-uri': ("'self'",),
        'form-action': ("'self'",),
        'frame-ancestors': ("'none'",),
        'upgrade-insecure-requests': True,
    }
}

# Production JWT settings - more secure
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # Shorter for production
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),     # Shorter for production
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
})

# Production caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'ssl_cert_reqs': None,
            },
        },
        'TIMEOUT': 300,
        'KEY_PREFIX': 'gatherhub_prod',
    }
}

# Production email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@gatherhub.com')

# Production static files
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/gatherhub/static/'

# Production media files
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/gatherhub/media/'

# Enhanced production logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'security': {
            'format': '{asctime} SECURITY {levelname} {module} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"time": "{asctime}", "level": "{levelname}", "module": "{module}", "message": "{message}"}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/gatherhub/django.log',
            'maxBytes': 1024*1024*50,  # 50MB
            'backupCount': 20,
            'formatter': 'verbose',
        },
        'security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/gatherhub/security.log',
            'maxBytes': 1024*1024*50,  # 50MB
            'backupCount': 20,
            'formatter': 'security',
        },
        'api': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/gatherhub/api.log',
            'maxBytes': 1024*1024*50,  # 50MB
            'backupCount': 20,
            'formatter': 'json',
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/gatherhub/error.log',
            'maxBytes': 1024*1024*50,  # 50MB
            'backupCount': 20,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security'],
            'level': 'WARNING',
            'propagate': False,
        },
        'gatherhub.security': {
            'handlers': ['security'],
            'level': 'INFO',
            'propagate': False,
        },
        'gatherhub': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'gatherhub.api': {
            'handlers': ['api'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Production channels layer
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [config('REDIS_URL')],
            'prefix': 'gatherhub_prod',
            'expiry': 60,
            'capacity': 2000,
            'channel_capacity': 50,
        },
    },
}

# Additional security headers for production
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Rate limiting - stricter for production
# These override the base settings
if 'gatherhub.middleware.APIRateLimitMiddleware' in MIDDLEWARE:
    # Production rate limits are defined in the middleware
    pass

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

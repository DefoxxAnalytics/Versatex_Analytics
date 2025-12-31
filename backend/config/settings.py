"""
Django settings for Analytics Dashboard
"""

import os
import sys
import logging
import secrets
from pathlib import Path
from datetime import timedelta
from decouple import config
from django.core.exceptions import ImproperlyConfigured

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security - CRITICAL: No default SECRET_KEY
def get_secret_key():
    """Get SECRET_KEY from environment, raise error if not set in production."""
    key = config('SECRET_KEY', default='')
    if not key:
        # Allow insecure key only in development with explicit DEBUG=True
        if config('DEBUG', default=False, cast=bool):
            logging.warning(
                "⚠️  Using insecure SECRET_KEY for development. "
                "Set SECRET_KEY environment variable for production!"
            )
            return 'django-insecure-dev-only-key-do-not-use-in-production'
        raise ImproperlyConfigured(
            "SECRET_KEY environment variable is required in production. "
            "Generate one with: python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
        )
    return key

SECRET_KEY = get_secret_key()

# CRITICAL: DEBUG defaults to False for security
DEBUG = config('DEBUG', default=False, cast=bool)

# Warn if DEBUG is True in a production-like environment
if DEBUG and 'runserver' not in sys.argv:
    logging.warning("⚠️  DEBUG=True detected outside of development server!")

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',

    # Local apps
    'apps.authentication',
    'apps.procurement',
    'apps.analytics',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'config.middleware.DeprecationMiddleware',  # Adds deprecation headers to legacy endpoints
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='analytics_db'),
        'USER': config('DB_USER', default='analytics_user'),
        'PASSWORD': config('DB_PASSWORD', default='analytics_pass'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Password Hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'  # EST/EDT
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File upload limits
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.authentication.backends.CookieJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        # Scoped throttle rates for specific operations
        'uploads': '10/hour',       # File upload rate limiting
        'exports': '30/hour',       # Export rate limiting
        'bulk_delete': '10/hour',   # Bulk delete rate limiting
        'login': '5/minute',        # Login rate limiting (backup to django-ratelimit)
        'read_api': '500/hour',     # Read operations rate limiting
    },
    'EXCEPTION_HANDLER': 'config.exception_handler.custom_exception_handler',
}

# JWT Settings - Reduced token lifetime for security
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),  # Reduced from 1 hour
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),     # Reduced from 7 days
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'UPDATE_LAST_LOGIN': True,
    # Cookie-based JWT settings for XSS protection
    'AUTH_COOKIE': 'access_token',
    'AUTH_COOKIE_REFRESH': 'refresh_token',
    'AUTH_COOKIE_DOMAIN': None,  # Use request domain
    'AUTH_COOKIE_SECURE': not DEBUG,  # HTTPS only in production
    'AUTH_COOKIE_HTTP_ONLY': True,  # Prevent JavaScript access
    'AUTH_COOKIE_PATH': '/',
    'AUTH_COOKIE_SAMESITE': 'Lax',
}

# CORS Settings - Strict configuration
# Parse allowed origins from environment
_cors_origins = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://localhost:5173'
).split(',')

# Helper to check if origin is for local development
def _is_local_origin(origin):
    """Check if origin is localhost or 127.0.0.1 (local development)"""
    return 'localhost' in origin or '127.0.0.1' in origin

# In production, only allow HTTPS origins (except for local development)
if not DEBUG:
    CORS_ALLOWED_ORIGINS = [
        origin.strip() for origin in _cors_origins
        if origin.strip().startswith('https://') or _is_local_origin(origin)
    ]
    # Warn if non-HTTPS origins are configured in production
    _insecure_origins = [o for o in _cors_origins if not o.strip().startswith('https://') and not _is_local_origin(o)]
    if _insecure_origins:
        logging.warning(f"⚠️  Insecure CORS origins configured (should use HTTPS): {_insecure_origins}")
else:
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in _cors_origins]

# Only allow credentials with explicit origin whitelist (not wildcards)
# IMPORTANT: CORS_ALLOW_CREDENTIALS should only be True if origins are explicitly listed
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False  # Never allow all origins with credentials

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Limit CORS methods to only what's needed
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# CSRF Settings
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:3000,http://localhost:5173'
).split(',')
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Session Security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 1800  # 30 minutes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Email Configuration
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@analytics.com')

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'Analytics Dashboard API',
    'DESCRIPTION': 'REST API for procurement analytics dashboard',
    'VERSION': '1.0.0',
}

# Security Settings - Always applied (not just in production)
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# Production Security Settings
if not DEBUG:
    # HTTPS enforcement
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HSTS - enforce HTTPS for 1 year
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Referrer policy
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

    # Prevent clickjacking
    X_FRAME_OPTIONS = 'DENY'

# Admin Site Configuration
# Dynamic admin URL: if not set, generate random path on each startup for security
_env_admin_url = config('ADMIN_URL', default='')
if _env_admin_url:
    ADMIN_URL = _env_admin_url if _env_admin_url.endswith('/') else f'{_env_admin_url}/'
else:
    # Generate dynamic admin URL for security (prevents enumeration)
    ADMIN_URL = f'manage-{secrets.token_hex(8)}/'
    logging.info(f"Dynamic admin URL generated: /{ADMIN_URL}")
LOGOUT_REDIRECT_URL = f'/{ADMIN_URL}login/'

# Frontend URL for "View Site" link in admin
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')

# Field Encryption (optional - for django-encrypted-model-fields)
# Generate key with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
FIELD_ENCRYPTION_KEY = config('FIELD_ENCRYPTION_KEY', default='')

# Logging configuration for security events
# Build handlers dict - only include file handler in production
_logging_handlers = {
    'console': {
        'class': 'logging.StreamHandler',
        'formatter': 'verbose',
    },
}

# Only add file handlers in production (non-DEBUG mode)
if not DEBUG:
    # Create logs directory if it doesn't exist
    (BASE_DIR / 'logs').mkdir(exist_ok=True)
    _logging_handlers['security_file'] = {
        'class': 'logging.FileHandler',
        'filename': BASE_DIR / 'logs' / 'security.log',
        'formatter': 'verbose',
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': _logging_handlers,
    'loggers': {
        'django.security': {
            'handlers': ['console', 'security_file'] if not DEBUG else ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
        'authentication': {
            'handlers': ['console', 'security_file'] if not DEBUG else ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# =============================================================================
# PRODUCTION SECURITY VALIDATION
# =============================================================================
# These checks run at startup to ensure critical security settings are configured
if not DEBUG:
    # Check for unchanged default passwords
    _db_password = config('DB_PASSWORD', default='')
    if 'MUST_CHANGE' in _db_password or 'CHANGE' in _db_password or _db_password == 'analytics_pass':
        raise ImproperlyConfigured(
            "DB_PASSWORD must be changed from the default value in production. "
            "Generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        )

    _redis_password = config('REDIS_PASSWORD', default='')
    if not _redis_password or 'MUST_CHANGE' in _redis_password or 'CHANGE' in _redis_password:
        raise ImproperlyConfigured(
            "REDIS_PASSWORD must be set to a strong value in production. "
            "Generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        )

    _secret_key = config('SECRET_KEY', default='')
    if 'MUST_CHANGE' in _secret_key or not _secret_key:
        raise ImproperlyConfigured(
            "SECRET_KEY must be set to a secure value in production. "
            "Generate with: python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
        )

    logging.info("Production security validation passed.")

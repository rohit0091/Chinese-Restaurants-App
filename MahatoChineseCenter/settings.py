"""
Django settings for MahatoChineseCenter project.
Production-ready configuration for CloudSentinel integration.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# SECURITY — all secrets come from environment variables, never hardcoded
# ---------------------------------------------------------------------------
import secrets

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')
if not SECRET_KEY or SECRET_KEY == 'unsafe-dev-key-change-in-production' or len(SECRET_KEY) < 32:
    # Auto-generate a secure random 50-character key so the app always boots safely
    SECRET_KEY = secrets.token_urlsafe(50)

DEBUG = os.environ.get('DEBUG', '0') == '1'

_raw_hosts = os.environ.get('ALLOWED_HOSTS', '*').split(',')
ALLOWED_HOSTS = [h.strip() for h in _raw_hosts if h.strip()]
for h in ['.trycloudflare.com', 'localhost', '127.0.0.1', 'cs-gateway']:
    if h not in ALLOWED_HOSTS and '*' not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(h)
if '*' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('*')

_raw_origins = os.environ.get('CSRF_TRUSTED_ORIGINS', 'https://*.trycloudflare.com,http://localhost:8081,http://127.0.0.1:8081').split(',')
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _raw_origins if o.strip()]
if 'https://*.trycloudflare.com' not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append('https://*.trycloudflare.com')

# Cloudflare Tunnel SSL proxy configuration
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # Ensure plain HTTP on localhost:8081 still works
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', '0') == '1'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', '0') == '1'

# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'cart',
    'home',
    'menu',
    'orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # <-- serves static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'MahatoChineseCenter.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_renderer',
            ],
        },
    },
]

WSGI_APPLICATION = 'MahatoChineseCenter.wsgi.application'

# ---------------------------------------------------------------------------
# Database — PostgreSQL when host is reachable, SQLite fallback for isolated tenants / local dev
# ---------------------------------------------------------------------------
_DB_HOST = os.environ.get('DB_HOST', '').strip()
_USE_POSTGRES = False
if _DB_HOST:
    import socket
    try:
        socket.gethostbyname(_DB_HOST)
        _USE_POSTGRES = True
    except Exception:
        _USE_POSTGRES = False

if _USE_POSTGRES:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'mahato'),
            'USER': os.environ.get('DB_USER', 'mahato'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': _DB_HOST,
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
else:
    # Isolated container / local development fallback
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & Media files
# ---------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = '/app/staticfiles'          # collectstatic target inside container
STATICFILES_DIRS = [BASE_DIR / 'static']  # source dir

# WhiteNoise compressed static serving
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media'                 # shared Docker volume mount point

# ---------------------------------------------------------------------------
# Auth redirects
# ---------------------------------------------------------------------------
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# ---------------------------------------------------------------------------
# Email (console backend for now)
# ---------------------------------------------------------------------------
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

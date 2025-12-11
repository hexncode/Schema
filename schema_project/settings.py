"""
Django settings for Schema project.
Includes GeoDjango configuration for GIS functionality.
"""

import os
from pathlib import Path
from datetime import timedelta

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use system env vars

# Heroku DATABASE_URL parsing
try:
    import dj_database_url
    HAS_DJ_DATABASE_URL = True
except ImportError:
    HAS_DJ_DATABASE_URL = False

# GDAL/GEOS configuration for Windows (PostGIS bundle includes these)
GDAL_LIBRARY_PATH = None
GEOS_LIBRARY_PATH = None

if os.name == 'nt':  # Windows
    # Try common PostGIS installation paths
    postgis_paths = [
        r'C:\Program Files\PostgreSQL\18\bin',
        r'C:\Program Files\PostgreSQL\17\bin',
        r'C:\Program Files\PostgreSQL\16\bin',
        r'C:\Program Files\PostgreSQL\15\bin',
        r'C:\OSGeo4W64\bin',
    ]
    for pg_path in postgis_paths:
        if os.path.exists(pg_path):
            os.environ['PATH'] = pg_path + ';' + os.environ.get('PATH', '')
            # Set GDAL_DATA if postgis bundle has it
            gdal_data = os.path.join(os.path.dirname(pg_path), 'share', 'gdal')
            if os.path.exists(gdal_data):
                os.environ['GDAL_DATA'] = gdal_data
            # Set explicit library paths for GeoDjango (Django settings)
            gdal_lib = os.path.join(pg_path, 'libgdal-35.dll')
            geos_lib = os.path.join(pg_path, 'libgeos_c.dll')
            if os.path.exists(gdal_lib):
                GDAL_LIBRARY_PATH = gdal_lib
            if os.path.exists(geos_lib):
                GEOS_LIBRARY_PATH = geos_lib
            break

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production-asdf123456')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Check if PostGIS mode is enabled (for conditional GeoDjango)
USE_POSTGIS = os.environ.get('USE_POSTGIS', 'False') == 'True'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Add GeoDjango only when PostGIS is enabled (requires GDAL)
if USE_POSTGIS:
    INSTALLED_APPS.insert(0, 'django.contrib.gis')

# Local apps
INSTALLED_APPS += [
    'atlas.apps.AtlasConfig',
    'cashflow.apps.CashflowConfig',
    'generator.apps.GeneratorConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'schema_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
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

WSGI_APPLICATION = 'schema_project.wsgi.application'

# Database Configuration
# Priority: DATABASE_URL (Heroku) > USE_POSTGIS env vars > SQLite

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL and HAS_DJ_DATABASE_URL:
    # Heroku Postgres - parse DATABASE_URL
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    # Override engine for PostGIS if USE_POSTGIS is set
    if USE_POSTGIS:
        DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'
elif USE_POSTGIS:
    # Local PostGIS configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': os.environ.get('DB_NAME', 'schema_gis'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
else:
    # SQLite for development (no GIS features in database)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Australia/Sydney'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# WhiteNoise for static files on Heroku
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
}

# Media files (user-uploaded content)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutes
    }
}

# For production with Redis:
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
#     }
# }

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_SECURE = not DEBUG  # Requires HTTPS in production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# GIS Layer configuration (file-based, no GDAL required for Django)
GIS_LAYERS_PATH = BASE_DIR / 'atlas' / 'gis' / 'Layers'

# GIS Cache configuration
GIS_CACHE_TTL_MINUTES = int(os.environ.get('GIS_CACHE_TTL_MINUTES', '15'))  # Cache lifetime
GIS_CACHE_MAX_ITEMS = int(os.environ.get('GIS_CACHE_MAX_ITEMS', '100'))  # Max cached items

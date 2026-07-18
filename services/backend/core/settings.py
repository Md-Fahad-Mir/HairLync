#=====================================================================
# Build paths inside the project like this: BASE_DIR / 'subdir'.
#=====================================================================
from pathlib import Path
from datetime import timedelta
import os
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env', override=True)


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def env_str(name, default=''):
    return os.environ.get(name, default).strip()


USE_S3 = env_bool('USE_S3', False)

#=====================================================================
# SECRET KEY SETTINGS
#=====================================================================
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-r*-_&00l_voaqtp-)ke-#xrjku14=8jpb_6$2hoo68prwsg!@q'
)


#=====================================================================
# DEBUG SETTINGS
#=====================================================================
DEBUG = env_bool('DJANGO_DEBUG', True)


#=====================================================================
# ALLOWED HOSTS SETTINGS
#=====================================================================
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')


#=====================================================================
# Application definition
#=====================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'drf_yasg',
    'corsheaders',

    # S3 media storage
    'storages',

    # Local apps
    'Apps.users',
    'Apps.profiles',
    'Apps.bookings',
    'Apps.reviews',
    'Apps.favorites',
    'Apps.subscriptions',
    'Apps.portfolio',
    'Apps.services',
    'Apps.recommendations',
    'Apps.education',
]



#=====================================================================
# Middleware Settings
#=====================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Serve collected static files (DRF/Swagger UI assets) under gunicorn with
    # DEBUG=False. Must sit right after SecurityMiddleware.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

#=====================================================================
# Root URL Config Settings
#=====================================================================
ROOT_URLCONF = 'core.urls'

#=====================================================================
# Template Settings
#=====================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

#=====================================================================
# WSGI Application Settings
#=====================================================================
WSGI_APPLICATION = 'core.wsgi.application'


#=====================================================================
# Database Settings
#=====================================================================
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}

#=====================================================================
# Custom User Model
#=====================================================================
AUTH_USER_MODEL = 'users.CustomUserModel'

#=====================================================================
# Password Validation Settings
#=====================================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


#=====================================================================
# Internationalization Settings
#=====================================================================
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


#=====================================================================
# Static Files Settings
#=====================================================================
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

#=====================================================================
# Media Files Settings
#=====================================================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

#=====================================================================
# File Storage Settings
#=====================================================================
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

if USE_S3:
    AWS_STORAGE_BUCKET_NAME = env_str('AWS_STORAGE_BUCKET_NAME')
    if not AWS_STORAGE_BUCKET_NAME:
        raise ImproperlyConfigured('USE_S3=True requires AWS_STORAGE_BUCKET_NAME.')

    AWS_S3_REGION_NAME = env_str('AWS_S3_REGION_NAME', env_str('AWS_REGION', 'eu-north-1'))
    AWS_S3_CUSTOM_DOMAIN = env_str('AWS_S3_CUSTOM_DOMAIN')
    AWS_LOCATION = env_str('AWS_LOCATION', 'media').strip('/')
    AWS_QUERYSTRING_AUTH = env_bool('AWS_QUERYSTRING_AUTH', False)
    AWS_S3_FILE_OVERWRITE = env_bool('AWS_S3_FILE_OVERWRITE', False)
    AWS_DEFAULT_ACL = None
    AWS_S3_SIGNATURE_VERSION = env_str('AWS_S3_SIGNATURE_VERSION', 's3v4')
    AWS_S3_ADDRESSING_STYLE = env_str('AWS_S3_ADDRESSING_STYLE', 'virtual')
    AWS_S3_ENDPOINT_URL = env_str('AWS_S3_ENDPOINT_URL') or None
    AWS_S3_VERIFY = env_bool('AWS_S3_VERIFY', True)

    AWS_ACCESS_KEY_ID = env_str('AWS_ACCESS_KEY_ID') or None
    AWS_SECRET_ACCESS_KEY = env_str('AWS_SECRET_ACCESS_KEY') or None
    AWS_SESSION_TOKEN = env_str('AWS_SESSION_TOKEN') or None

    cache_control = env_str('AWS_S3_CACHE_CONTROL', 'max-age=86400')
    AWS_S3_OBJECT_PARAMETERS = {}
    if cache_control:
        AWS_S3_OBJECT_PARAMETERS['CacheControl'] = cache_control

    STORAGES['default'] = {
        'BACKEND': 'storages.backends.s3.S3Storage',
    }

    if AWS_S3_CUSTOM_DOMAIN:
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
    elif AWS_S3_REGION_NAME:
        MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/{AWS_LOCATION}/'
    else:
        MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{AWS_LOCATION}/'

#=====================================================================
# Default Auto Field
#=====================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#=====================================================================
# Swagger Settings 
#=====================================================================
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header using Bearer scheme. Example: "Bearer {token}"'
        },
        'Basic': {
            'type': 'basic'
        }
    },
    'USE_SESSION_AUTH': True,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
    'OPERATIONS_SORTER': 'alpha',
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'none',
    'DEEP_LINKING': True,
    'SHOW_EXTENSIONS': True,
    'DEFAULT_MODEL_RENDERING': 'model',
    'DEFAULT_MODEL_DEPTH': 3,
}

#=====================================================================
# REST Framework Settings
#=====================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    'EXCEPTION_HANDLER': 'Apps.users.utils.custom_exception_handler',
}

#=====================================================================
# Simple JWT Settings
#=====================================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'TOKEN_TYPE_CLAIM': 'token_type',
}

#=====================================================================
# CORS Settings
#=====================================================================
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS', 'http://localhost:3000'
).split(',')

#=====================================================================
# CSRF Settings
#=====================================================================
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'https://api.hairlync.com,https://hairlync.com,https://admin.hairlync.com,http://localhost:8000,http://127.0.0.1:8000'
).split(',')

#=====================================================================
# Email Settings (Console backend for development)
#=====================================================================
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() in ('true', '1')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@hairlync.com')

#=====================================================================
# Stripe Settings
#=====================================================================
STRIPE_SECRET_KEY = env_str('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = env_str('STRIPE_PUBLISHABLE_KEY')
STRIPE_WEBHOOK_SECRET = env_str('STRIPE_WEBHOOK_SECRET')
STRIPE_CHECKOUT_SUCCESS_URL = env_str(
    'STRIPE_CHECKOUT_SUCCESS_URL', 'https://hairlync.com/billing/success'
)
STRIPE_CHECKOUT_CANCEL_URL = env_str(
    'STRIPE_CHECKOUT_CANCEL_URL', 'https://hairlync.com/billing/cancel'
)
STRIPE_BILLING_PORTAL_RETURN_URL = env_str(
    'STRIPE_BILLING_PORTAL_RETURN_URL', 'https://hairlync.com/account'
)

#=====================================================================
# Logging Settings
#=====================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'Apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
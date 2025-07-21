import os
from pathlib import Path
import ssl
import certifi
import dj_database_url

ssl_context = ssl.create_default_context(cafile=certifi.where())

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-so%v9*$eloe^!7w9tai1phx87q-w%xvgr=g@19nylb7_!!($jw"

DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "transport-2-0imo.onrender.com",  # ✅ your Render backend domain
    "transport-frontend-jet.vercel.app",  # ✅ your Vercel frontend domain
    "postman",
]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",

    "accounts",
    "travels",
    "booking",
    "reviews",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "travelshare.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "travelshare.wsgi.application"

# ✅ DATABASE CONFIGURATION
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', 'postgres://transport_db_09hl_user:WuFX5Bk3TLUg4gbsKnKi7HNHwt8UqsfS@dpg-d1v2g3ndiees73b8c2u0-a.oregon-postgres.render.com:5432/transport_db_09hl'),
        conn_max_age=600,
        ssl_require=True
    )
}

# REST framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_USER_MODEL = 'accounts.CustomUser'

# Media
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Static files
STATIC_URL = 'static/'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://transport-frontend-jet.vercel.app",
]

CSRF_TRUSTED_ORIGINS = [
    "https://transport-frontend-jet.vercel.app",
    "https://transport-2-0imo.onrender.com",
]

# Email backend (Gmail App Password)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tunde200.james@gmail.com'
EMAIL_HOST_PASSWORD = 'hnta tpgr idwo yrbg'  # App Password (secure in env on production)

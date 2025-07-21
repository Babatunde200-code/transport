from pathlib import Path
import ssl
import certifi
import os

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

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'transport',
        'USER': 'postgres',
        'PASSWORD': 'PeruPara',
        'HOST': 'localhost',
        'PORT': '5432',
    }
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
CORS_ALLOW_ALL_ORIGINS = False  # ❌ safer in production
CORS_ALLOWED_ORIGINS = [
    "https://transport-frontend-jet.vercel.app",  # ✅ your frontend
]

CSRF_TRUSTED_ORIGINS = [
    "https://transport-frontend-jet.vercel.app",
    "https://transport-2-0imo.onrender.com",
]

# Email backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tunde200.james@gmail.com'
EMAIL_HOST_PASSWORD = 'hnta tpgr idwo yrbg'  # ✅ Gmail App Password

from pathlib import Path
import certifi
from pymongo import MongoClient
import environ
import os
from datetime import timedelta


# env setup
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialise environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# MongoDB
MONGO_URI = env("MONGO_URI")
MONGO_DB_NAME = env("MONGO_DB_NAME")

# ==========================
# SECURITY
# ==========================
SECRET_KEY = env("SECRET_KEY", default="change-me")
DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "asaptravels.ng",
    "www.asaptravels.ng",
    "transport-2-0imo.onrender.com",
    ".onrender.com",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://asaptravels.ng",
    "https://www.asaptravels.ng",
    "https://transport-2-0imo.onrender.com",
    "https://transport-frontend-jet.vercel.app",
]


# ==========================
# INSTALLED APPS
# ==========================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",

    # Third-party
    "rest_framework",
    "corsheaders",
    "rest_framework_simplejwt.token_blacklist",

    # Local apps
    "accounts",
    "travels",
]

# ==========================
# MIDDLEWARE
# ==========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",

    # CORS
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "middleware.csrf_disable.DisableCSRFMiddleware",
]

# ==========================
# CORS CONFIG
# ==========================
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_HEADERS = ["*"]
    CORS_ALLOW_METHODS = ["*"]
else:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://asaptravels.ng",
        "https://www.asaptravels.ng",
        "https://transport-frontend-jet.vercel.app",
    ]
    CORS_ALLOWED_ORIGIN_REGEXES = [
        r"^https://.*\.asaptravels\.ng$",
    ]

# ==========================
# TEMPLATES
# ==========================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ROOT_URLCONF = "travelshare.urls"

# ==========================
# REST FRAMEWORK
# ==========================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.auth_backend.PyMongoJWTAuthentication",
        "travels.auth.PyMongoJWTAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# ==========================
# JWT
# ==========================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

# ==========================
# DATABASES
# ==========================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ==========================
# STATIC FILES
# ==========================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (Images, videos, etc.)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# For production on Render
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# ==========================
# EMAIL (Optional)
# ==========================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

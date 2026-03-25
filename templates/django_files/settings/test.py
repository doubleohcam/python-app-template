"""Test settings for {app_name} project.

Standalone settings for testing - no environment variables required.
Uses SQLite in-memory for fast, self-contained tests.
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Test secret key - only used in tests
SECRET_KEY = "test-secret-key-not-for-production"

# Admin credentials for test superuser creation
DJANGO_ADMIN_USERNAME = "testadmin"
DJANGO_ADMIN_PASSWORD = "testpassword"

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Database - SQLite in-memory for fast, self-contained tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party apps
    "django_extensions",
    "pghistory",
    "pgtrigger",
    # local apps
    "{app_name_config}",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "{app_name}.urls"

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

WSGI_APPLICATION = "{app_name}.wsgi.application"

# Password validation - simplified for tests
AUTH_PASSWORD_VALIDATORS = []

# Faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Time constants (used by models)
MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR

# Disable logging during tests
LOGGING = {}

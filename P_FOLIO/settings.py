import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-idysu!216q=mto__y(bjr1wpd3_98$f4_6pu*grsvj)jvya-&3"

DEBUG = os.getenv("PRODUCTION", "False").lower() not in ("1", "true", "yes")

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOST", "127.0.0.1,localhost,esta-sensate-unquickly.ngrok-free.dev"
    ).split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "portfolio",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "portfolio.middleware.PageViewMiddleware",
]

ROOT_URLCONF = "P_FOLIO.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "utility.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "P_FOLIO.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


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


LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Lagos"

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}


# File-based cache: the analytics middleware increments counters here, then the
# flush endpoint / management command writes them to the database every 5 min.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR / ".cache",
        "TIMEOUT": 60 * 60 * 24 * 7,
        "OPTIONS": {"MAX_ENTRIES": 5000},
    }
}


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Authentication routes for the owner area.
LOGIN_URL = "portfolio:login"
LOGIN_REDIRECT_URL = "portfolio:custom_admin"
LOGOUT_REDIRECT_URL = "portfolio:home"


# The CV is embedded same-origin, so DENY would block our own iframe.
X_FRAME_OPTIONS = "SAMEORIGIN"

# Cookies are only marked secure when running outside DEBUG. Production must
# be served over HTTPS (Render, Fly, etc. all provide it).
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

FULL_DOMAIN = os.getenv("FULL_DOMAIN", "http://localhost:8000").rstrip("/")

# Token used by the external 5-minute cron job that calls the analytics flush
# endpoint. Set this in production; the endpoint refuses to run without it.
ANALYTICS_FLUSH_TOKEN = os.getenv("ANALYTICS_FLUSH_TOKEN", "")

# Number of days of aggregated page-view rows kept by the dashboard query.
ANALYTICS_WINDOW_DAYS = 30

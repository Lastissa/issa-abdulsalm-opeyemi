import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-idysu!216q=mto__y(bjr1wpd3_98$f4_6pu*grsvj)jvya-&3"

DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOST", "localhost").split(",")

CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "https://localhost:8000, https://esta-sensate-unquickly.ngrok-free.dev/").split(",")

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
    "_"
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
                "service_internal.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "P_FOLIO.wsgi.application"


if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["DB_NAME"],
            "USER": os.environ["DB_USER"],
            "PASSWORD": os.environ["DB_PASSWORD"],
            "HOST": os.environ["DB_HOST"],
            "PORT": os.getenv("DB_PORT", "5432"),
            "OPTIONS": {"sslmode": os.getenv("DB_SSLMODE", "require")},
            "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),
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

if DEBUG:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }
else:
    AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
    AWS_STORAGE_BUCKET_NAME = os.environ["S3_BUCKET"]
    AWS_S3_REGION_NAME = os.environ["AWS_REGION"]
    AWS_S3_ENDPOINT_URL = os.environ["AWS_ENDPOINT_URL_S3"]
    AWS_S3_ADDRESSING_STYLE = "path"
    AWS_LOCATION = "media"
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }


# Using locmeme for dev/ will move to redis for prod
# flush endpoint / management command writes them to the database every 5 min.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "opeyemi-01",
        "TIMEOUT": 60 * 60 * 24 * 7,            # 7 days in seconds
        "OPTIONS": {
            "MAX_ENTRIES": 5000                 # Automatically purges old keys when reached
        }
    }
}


LOGIN_URL = "portfolio:login"
LOGIN_REDIRECT_URL = "portfolio:custom_admin"
LOGOUT_REDIRECT_URL = "portfolio:home"


# The CV is embedded same-origin, same origin mean only domain from this same domain can iframe it.
X_FRAME_OPTIONS = "SAMEORIGIN"

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

FULL_DOMAIN = ALLOWED_HOSTS[0]

# Token used by the external 5-minute cron job that calls the analytics flush
# endpoint. Set this in production; the endpoint refuses to run without it.
SY_SECRET = os.getenv("SY_SECRET", "")

# Number of days of aggregated page-view rows kept by the dashboard query.
ANALYTICS_WINDOW_DAYS = int(os.getenv("ANALYTICS_WINDOW_DAYS", "30"))

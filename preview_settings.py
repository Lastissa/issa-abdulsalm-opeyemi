from P_FOLIO.settings import *  # noqa: F403,F401

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / ".preview.sqlite3",  # noqa: F405
    }
}
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR / ".preview-cache",  # noqa: F405
        "TIMEOUT": 60 * 60 * 24 * 7,
        "OPTIONS": {"MAX_ENTRIES": 5000},
    }
}
MEDIA_ROOT = BASE_DIR / ".preview-media"  # noqa: F405
ANALYTICS_FLUSH_TOKEN = "preview-token"
FULL_DOMAIN = "http://127.0.0.1:8011"

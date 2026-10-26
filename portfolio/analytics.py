"""Cache-backed analytics.

Every public page view increments counters in the file-based cache. Nothing
touches the database during the request. A cron job calls the flush endpoint
(or ``manage.py flush_analytics``) every five minutes to move the accumulated
numbers into ``PageView`` and ``Visitor`` rows.
"""

from __future__ import annotations

import hashlib
import logging
import re
from datetime import date, datetime
from urllib.parse import urlparse

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import PageView, Visitor

logger = logging.getLogger(__name__)

CACHE_PREFIX = "analytics"
DATES_KEY = f"{CACHE_PREFIX}:dates"
LOCK_KEY = f"{CACHE_PREFIX}:flush_lock"
CACHE_TIMEOUT = 60 * 60 * 24 * 7

BOT_RE = re.compile(
    r"(bot|crawler|spider|slurp|bingpreview|facebookexternalhit|headless|"
    r"python-requests|curl|wget|scrapy|semrush|ahrefs)",
    re.IGNORECASE,
)

EXCLUDED_PREFIXES = (
    "/admin/",
    "/custom-admin/",
    "/login/",
    "/logout/",
    "/static/",
    "/media/",
    "/api/",
    "/feed/new/",
    "/feed/rss/",
    "/cv/file/",
    "/cv/download/",
)

EXCLUDED_EXACT = {
    "/robots.txt",
    "/llms.txt",
    "/sitemap.xml",
    "/favicon.ico",
    "/site.webmanifest",
}

EXCLUDED_SUFFIXES = (
    ".css",
    ".js",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".svg",
    ".ico",
    ".xml",
    ".txt",
    ".json",
    ".webmanifest",
    ".pdf",
)


def is_trackable(path: str, user_agent: str = "") -> bool:
    if not path or not path.startswith("/"):
        return False
    if path in EXCLUDED_EXACT:
        return False
    if path.startswith(EXCLUDED_PREFIXES):
        return False
    if path.lower().endswith(EXCLUDED_SUFFIXES):
        return False
    if user_agent and BOT_RE.search(user_agent):
        return False
    return True


def make_visitor_hash(raw_id: str) -> str:
    return hashlib.sha256(
        f"{raw_id}:{settings.SECRET_KEY}".encode("utf-8")
    ).hexdigest()[:20]


def _today_key() -> str:
    return timezone.localdate().isoformat()


def _views_key(day: str, path: str) -> str:
    return f"{CACHE_PREFIX}:views:{day}:{path}"


def _paths_key(day: str) -> str:
    return f"{CACHE_PREFIX}:paths:{day}"


def _visitors_key(day: str) -> str:
    return f"{CACHE_PREFIX}:visitors:{day}"


def _increment(key: str, amount: int = 1) -> None:
    if cache.add(key, amount, timeout=CACHE_TIMEOUT):
        return
    try:
        cache.incr(key, amount)
    except ValueError:
        cache.set(key, amount, timeout=CACHE_TIMEOUT)


def _add_to_registry(key: str, value: str) -> None:
    values = cache.get(key) or []
    if value not in values:
        values.append(value)
        cache.set(key, values, timeout=CACHE_TIMEOUT)


def record_view(
    path: str,
    raw_visitor_id: str,
    user_agent: str = "",
    referrer: str = "",
) -> None:
    """Increment the cache counters for one page view."""
    path = path[:255]
    day = _today_key()
    visitor_hash = make_visitor_hash(raw_visitor_id)

    _increment(_views_key(day, path))
    _add_to_registry(DATES_KEY, day)
    _add_to_registry(_paths_key(day), path)

    visitors = cache.get(_visitors_key(day)) or {}
    now = timezone.now().isoformat()
    referrer_host = ""
    if referrer:
        try:
            referrer_host = urlparse(referrer).netloc[:200]
        except ValueError:
            referrer_host = ""

    entry = visitors.get(visitor_hash) or {
        "views": 0,
        "first_seen": now,
        "last_seen": now,
        "last_path": path,
        "user_agent": "",
        "referrer": "",
    }
    entry["views"] = int(entry.get("views", 0)) + 1
    entry["last_seen"] = now
    entry["last_path"] = path[:255]
    if user_agent:
        entry["user_agent"] = user_agent[:300]
    if referrer_host:
        entry["referrer"] = referrer_host
    visitors[visitor_hash] = entry
    cache.set(_visitors_key(day), visitors, timeout=CACHE_TIMEOUT)


def pending_snapshot() -> dict:
    """Read the unflushed cache counters for the dashboard."""
    days = cache.get(DATES_KEY) or []
    total_views = 0
    total_paths = 0
    total_visitors = 0
    for day in days:
        paths = cache.get(_paths_key(day)) or []
        for path in paths:
            total_views += cache.get(_views_key(day, path)) or 0
            total_paths += 1
        total_visitors += len(cache.get(_visitors_key(day)) or {})
    return {
        "views": total_views,
        "paths": total_paths,
        "visitors": total_visitors,
        "days": len(days),
    }


def _parse_datetime(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def _clear_cache(days: list[str]) -> None:
    keys = [DATES_KEY]
    for day in days:
        keys.append(_paths_key(day))
        keys.append(_visitors_key(day))
        for path in cache.get(_paths_key(day)) or []:
            keys.append(_views_key(day, path))
    cache.delete_many(keys)


def flush() -> dict:
    """Move cached counters into the database. Safe to call concurrently."""
    if not cache.add(LOCK_KEY, "1", timeout=300):
        return {"ok": False, "error": "flush_already_running"}

    summary = {
        "ok": True,
        "days": 0,
        "page_rows": 0,
        "visitor_rows": 0,
        "views": 0,
    }
    days = list(cache.get(DATES_KEY) or [])

    try:
        with transaction.atomic():
            for day_key in days:
                try:
                    day = date.fromisoformat(day_key)
                except (TypeError, ValueError):
                    continue

                for path in list(cache.get(_paths_key(day_key)) or []):
                    count = cache.get(_views_key(day_key, path)) or 0
                    if count <= 0:
                        continue
                    row, created = PageView.objects.get_or_create(
                        path=path[:255],
                        date=day,
                    )
                    if created:
                        row.views = count
                        row.save(update_fields=["views"])
                    else:
                        PageView.objects.filter(pk=row.pk).update(
                            views=F("views") + count
                        )
                    summary["views"] += count
                    summary["page_rows"] += 1

                visitors = cache.get(_visitors_key(day_key)) or {}
                for visitor_hash, data in visitors.items():
                    if not data:
                        continue
                    first_seen = _parse_datetime(data.get("first_seen"))
                    last_seen = _parse_datetime(data.get("last_seen"))
                    views = int(data.get("views") or 0)
                    if not first_seen or not last_seen or views <= 0:
                        continue

                    row, created = Visitor.objects.get_or_create(
                        visitor_hash=visitor_hash[:64],
                        defaults={
                            "first_seen": first_seen,
                            "last_seen": last_seen,
                            "views": views,
                            "last_path": (data.get("last_path") or "")[:255],
                            "user_agent": (data.get("user_agent") or "")[:300],
                            "referrer": (data.get("referrer") or "")[:200],
                        },
                    )
                    if not created:
                        Visitor.objects.filter(pk=row.pk).update(
                            views=F("views") + views,
                            last_seen=last_seen,
                            last_path=(data.get("last_path") or "")[:255],
                            user_agent=(data.get("user_agent") or "")[:300],
                            referrer=(data.get("referrer") or "")[:200],
                        )
                    summary["visitor_rows"] += 1

                summary["days"] += 1

        _clear_cache(days)
        return summary
    except Exception:
        logger.exception("analytics: flush failed")
        raise
    finally:
        cache.delete(LOCK_KEY)

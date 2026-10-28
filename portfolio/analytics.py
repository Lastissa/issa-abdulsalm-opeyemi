"""Cache-backed analytics.

Every public page view increments counters in the cache. Nothing
touches the database during the request. A cron job calls the flush endpoint
(or ``manage.py flush_analytics``) every five minutes to move the accumulated
numbers into ``PageView`` and ``Visitor`` rows.
"""

import hashlib
import re
from datetime import date, datetime
from urllib.parse import urlparse

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import PageView, Visitor

from service_internal.caches import get_cache, set_cache, del_cache
from service_internal.logger import error_logger

CACHE_PREFIX = "analytics"
DATES_KEY = f"{CACHE_PREFIX}:dates"
LOCK_KEY = f"{CACHE_PREFIX}:cache_to_db_transfer_in_progress"
CACHE_TIMEOUT = 60 * 60 * 24 * 7 # a week


BOT_RE = re.compile(
    r"("
    # General bots and crawlers
    r"bot|crawler|spider|slurp|"
    r"bingpreview|headless|"

    # Search engines
    r"googlebot|googleother|google-extended|"
    r"adsbot-google|mediapartners-google|"
    r"bingbot|msnbot|duckduckbot|duckassistbot|"
    r"baiduspider|yandexbot|sogou|exabot|"
    r"applebot|applebot-extended|petalbot|"
    r"360spider|yisouspider|"

    # AI crawlers and AI assistants
    r"gptbot|chatgpt-user|oai-searchbot|oai-adsbot|"
    r"claudebot|claude-searchbot|claude-user|"
    r"anthropic-ai|claude-web|"
    r"perplexitybot|perplexity-user|"
    r"bytespider|ccbot|cohere-ai|"
    r"meta-externalagent|meta-externalfetcher|"
    r"meta-webindexer|mistralai|mistral-ai|"
    r"amazonbot|youbot|diffbot|"

    # Social media and link previews
    r"facebookexternalhit|facebookbot|"
    r"twitterbot|linkedinbot|"
    r"telegrambot|whatsapp|slackbot|"
    r"discordbot|embedly|quora link preview|"

    # SEO and website auditing tools
    r"semrush|ahrefs|mj12bot|dotbot|"
    r"blexbot|dataforseobot|serpstatbot|"
    r"rogerbot|linkdexbot|seznambot|"
    r"screaming frog|siteauditbot|"
    r"megaindex|netpeak|"

    # HTTP clients and scraping libraries
    r"python-requests|python-httpx|"
    r"aiohttp|curl|wget|scrapy|"
    r"go-http-client|node-fetch|"
    r"axios|okhttp|libwww-perl|"
    r"java/|postmanruntime|insomnia|"

    # Automated browsers and testing tools
    r"headlesschrome|phantomjs|"
    r"selenium|playwright|puppeteer|"
    r"webdriver|browserless|"

    # Monitoring and uptime checks
    r"uptimerobot|pingdom|statuscake|"
    r"site24x7|datadog|"

    # Archives and other automated services
    r"ia_archiver|archive\.org_bot|"
    r"turnitinbot|censysinspect|"
    r"shodan|nikto|sqlmap"
    r")",
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
    return hashlib.sha256(f"{raw_id}:{settings.SECRET_KEY}".encode("utf-8")).hexdigest()[:20]


def _today_key() -> str:
    "return today localdate in iso format"
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
    values = get_cache(key) or []
    if value not in values:
        values.append(value)
        cache.set(key, values, timeout=CACHE_TIMEOUT)


def record_view(path: str,raw_visitor_id: str,user_agent: str = "",referrer: str = "",) -> None:
    """Increment the cache counters for one page view."""
    path = path[:255]
    day = _today_key()
    visitor_hash = make_visitor_hash(raw_visitor_id)

    _increment(_views_key(day, path))
    _add_to_registry(DATES_KEY, day)
    _add_to_registry(_paths_key(day), path)

    visitors = get_cache(_visitors_key(day)) or {}
    now = timezone.now().isoformat()
    referrer_host = ""
    if referrer:
        try:
            referrer_host = urlparse(referrer).netloc[:200] # first 200 char of the domain name
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
    days = get_cache(DATES_KEY) or []
    total_views = 0
    total_paths = 0
    total_visitors = 0
    for day in days:
        paths = get_cache(_paths_key(day)) or []
        for path in paths:
            total_views += get_cache(_views_key(day, path)) or 0
            total_paths += 1
        total_visitors += len(get_cache(_visitors_key(day)) or {})
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
        for path in get_cache(_paths_key(day)) or []:
            keys.append(_views_key(day, path))
    cache.delete_many(keys)


def flush_caches_count_to_db() -> dict:
    """Move cached counters into the database. Safe to call concurrently."""
    
    if not cache.add(LOCK_KEY, "1", timeout=300):
        return {"ok": False, "error": "cache_to_db_tranfer_already_running"}

    summary = {
        "ok": True,
        "days": 0,
        "page_rows": 0,
        "visitor_rows": 0,
        "views": 0,
    }
    days = sorted(get_cache(DATES_KEY) or [])

    try:
        with transaction.atomic():
            for day_key in days:
                try:
                    day = date.fromisoformat(day_key)
                except (TypeError, ValueError):
                    continue

                for path in list(get_cache(_paths_key(day_key)) or []):
                    count = get_cache(_views_key(day_key, path)) or 0
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

                visitors = get_cache(_visitors_key(day_key)) or {}
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
        error_logger("ANALYTICS: cache transfer to database failed")
        raise
    finally:
        del_cache(LOCK_KEY)

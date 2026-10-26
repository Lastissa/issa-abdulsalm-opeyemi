import logging
import uuid

from django.conf import settings

from .analytics import is_trackable, record_view

logger = logging.getLogger(__name__)

VISITOR_COOKIE = "pv_id"
VISITOR_COOKIE_AGE = 60 * 60 * 24 * 365


class PageViewMiddleware:
    """Count public page views in the cache, never do so in the database."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            if self._should_track(request, response):
                raw_id = request.COOKIES.get(VISITOR_COOKIE, "")
                if not raw_id or len(raw_id) < 16:
                    raw_id = uuid.uuid4().hex
                    response.set_cookie(
                        VISITOR_COOKIE,
                        raw_id,
                        max_age=VISITOR_COOKIE_AGE,
                        httponly=True,
                        samesite="Lax",
                        secure=request.is_secure(),
                    )
                record_view(
                    request.path,
                    raw_id,
                    request.META.get("HTTP_USER_AGENT", ""),
                    request.META.get("HTTP_REFERER", ""),
                )
        except Exception:
            # Analytics must never break a page render.
            logger.exception("analytics: could not record page view")

        return response

    @staticmethod
    def _should_track(request, response):
        if request.method != "GET":
            return False
        if response.status_code >= 400:
            return False
        if getattr(response, "streaming", False):
            return False
        if request.user.is_authenticated and request.user.is_staff:
            return False
        if request.path.startswith(settings.STATIC_URL):
            return False
        if request.path.startswith(settings.MEDIA_URL):
            return False
        return is_trackable(request.path, request.META.get("HTTP_USER_AGENT", ""))

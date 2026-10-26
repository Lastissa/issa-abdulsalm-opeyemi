"""Modern sitemap: real URLs, accurate lastmod, no ignored priority/changefreq."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone

from .data import PROJECTS
from .models import CVVersion, FeedPost


class PortfolioSitemap(Sitemap):
    protocol = "https"

    def items(self):
        latest_post = (
            FeedPost.objects.filter(is_published=True)
            .order_by("-updated_at")
            .first()
        )
        latest_cv = CVVersion.objects.filter(is_active=True).first()

        entries = [
            {"name": "portfolio:home", "lastmod": None},
            {"name": "portfolio:projects", "lastmod": None},
            {
                "name": "portfolio:feed",
                "lastmod": latest_post.updated_at if latest_post else None,
            },
            {
                "name": "portfolio:cv",
                "lastmod": latest_cv.uploaded_at if latest_cv else None,
            },
        ]
        entries.extend(
            {
                "name": "portfolio:project_detail",
                "args": [project["slug"]],
                "lastmod": None,
            }
            for project in PROJECTS
        )
        return entries

    def location(self, item):
        return reverse(item["name"], args=item.get("args", []))

    def lastmod(self, item):
        value = item.get("lastmod")
        if value and timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.get_current_timezone())
        return value

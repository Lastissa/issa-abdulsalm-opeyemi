"""
portfolio/sitemaps.py

Three real pages, three sitemap entries. Wired into P_FOLIO/urls.py at
/sitemap.xml. See workflow.md, decision S1.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    protocol = "https"

    def items(self):
        # (url name, priority)
        return [
            ("portfolio:landing", 1.0),
            ("portfolio:projects", 0.9),
            ("portfolio:cv", 0.7),
        ]

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]

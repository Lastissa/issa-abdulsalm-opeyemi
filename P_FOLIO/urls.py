from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from portfolio import views as portfolio_views
from portfolio.sitemaps import StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("portfolio.urls")),
    path("sitemap.xml",sitemap,{"sitemaps": sitemaps}, name = "sitemap"),
    path("robots.txt", portfolio_views.robots_txt, name="robots_txt"),
    path("llms.txt", portfolio_views.llms_txt, name="llms_txt"),
]

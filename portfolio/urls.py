from django.urls import path
from django.views.generic.base import RedirectView

from . import views

from .views import *
urlpatterns = [
    path("sitemap.xml", SitemapView.as_view(), name="sitemap"),
    path("favicon.ico", RedirectView.as_view(url="/static/images/favicon.ico"), name="favicon"),
    path("", views.HomeView.as_view(), name="home"),
]

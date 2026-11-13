from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("_admin/", admin.site.urls),
    path("sy/", include("_.urls")),
    path("", include("portfolio.urls")),

]
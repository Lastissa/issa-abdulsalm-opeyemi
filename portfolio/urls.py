from django.urls import path

from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("projects/", views.projects, name="projects"),
    path("cv/", views.cv_view, name="cv"),
    path("cv/download/", views.cv_download, name="cv_download"),
]

from django.urls import path

from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.home, name="home"),
    path("projects/", views.projects, name="projects"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
    path("feed/", views.feed, name="feed"),
    path("feed/rss/", views.feed_rss, name="feed_rss"),
    path("feed/new/", views.feed_create, name="feed_create"),
    path("feed/<int:pk>/edit/", views.feed_edit, name="feed_edit"),
    path("feed/<int:pk>/delete/", views.feed_delete, name="feed_delete"),
    path("cv/", views.cv_view, name="cv"),
    path("cv/file/", views.cv_file, name="cv_file"),
    path("cv/download/", views.cv_download, name="cv_download"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("custom-admin/", views.custom_admin_dashboard, name="custom_admin"),
    path(
        "custom-admin/visitors/",
        views.custom_admin_visitors,
        name="custom_admin_visitors",
    ),
    path(
        "custom-admin/visitors/export/",
        views.custom_admin_visitors_export,
        name="custom_admin_visitors_export",
    ),
    path(
        "custom-admin/visitors/<int:pk>/delete/",
        views.custom_admin_visitor_delete,
        name="custom_admin_visitor_delete",
    ),
    path("custom-admin/posts/", views.custom_admin_posts, name="custom_admin_posts"),
    path(
        "custom-admin/posts/<int:pk>/delete/",
        views.custom_admin_post_delete,
        name="custom_admin_post_delete",
    ),
    path("custom-admin/cv/", views.custom_admin_cv, name="custom_admin_cv"),
    path(
        "custom-admin/cv/<int:pk>/activate/",
        views.custom_admin_cv_activate,
        name="custom_admin_cv_activate",
    ),
    path(
        "custom-admin/cv/<int:pk>/delete/",
        views.custom_admin_cv_delete,
        name="custom_admin_cv_delete",
    ),
    path(
        "custom-admin/api/analytics/flush/",
        views.analytics_flush,
        name="analytics_flush",
    ),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("llms.txt", views.llms_txt, name="llms_txt"),
]

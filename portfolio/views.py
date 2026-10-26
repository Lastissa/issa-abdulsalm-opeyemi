import csv
import hashlib
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Sum
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.http import (
    content_disposition_header,
    url_has_allowed_host_and_scheme,
)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
)

from utility import config

from .analytics import flush, pending_snapshot
from .data import PROJECTS, featured_projects, get_project
from .forms import CVUploadForm, FeedPostForm, LoginForm
from .models import CVVersion, FeedPost, PageView, Visitor

CV_STATIC_DIR = Path(settings.BASE_DIR) / "portfolio" / "static" / "portfolio" / "files"
LOGIN_ATTEMPT_LIMIT = 6
LOGIN_ATTEMPT_WINDOW = 60 * 10

staff_required = user_passes_test(
    lambda user: user.is_active and user.is_staff,
    login_url="portfolio:login",
)


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------


def home(request):
    latest_posts = FeedPost.objects.filter(is_published=True).select_related(
        "author"
    )[:3]
    return render(
        request,
        "portfolio/home.html",
        {
            "featured_projects": featured_projects(3),
            "latest_posts": latest_posts,
        },
    )


def projects(request):
    return render(
        request,
        "portfolio/projects.html",
        {"projects": PROJECTS},
    )


def project_detail(request, slug):
    project = get_project(slug)
    if not project:
        raise Http404("Project not found")
    related = [item for item in PROJECTS if item["slug"] != slug][:3]
    return render(
        request,
        "portfolio/project_detail.html",
        {"project": project, "related_projects": related},
    )


def _feed_context(request, form=None):
    posts = FeedPost.objects.filter(is_published=True).select_related("author")
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return {
        "page_obj": page_obj,
        "posts": page_obj.object_list,
        "form": form or FeedPostForm(),
        "post_count": posts.count(),
    }


def feed(request):
    return render(request, "portfolio/feed.html", _feed_context(request))


@staff_required
@require_POST
def feed_create(request):
    form = FeedPostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, "Post published.")
        return redirect(post.get_absolute_url())

    messages.error(request, "The post could not be published. Check the fields below.")
    return render(
        request,
        "portfolio/feed.html",
        _feed_context(request, form=form),
        status=400,
    )


@staff_required
@require_http_methods(["GET", "POST"])
def feed_edit(request, pk):
    post = get_object_or_404(FeedPost, pk=pk)
    if request.method == "POST":
        form = FeedPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated.")
            return redirect(post.get_absolute_url())
    else:
        form = FeedPostForm(instance=post)
    return render(
        request,
        "portfolio/feed_edit.html",
        {"form": form, "post": post},
    )


@staff_required
@require_POST
def feed_delete(request, pk):
    post = get_object_or_404(FeedPost, pk=pk)
    post.delete()
    messages.success(request, "Post deleted.")
    return redirect("portfolio:feed")


@require_GET
def feed_rss(request):
    posts = FeedPost.objects.filter(is_published=True).select_related("author")[:50]
    feed_url = request.build_absolute_uri(reverse("portfolio:feed"))
    rss = Rss201rev2Feed(
        title=f"{config.FULL_NAME} - Feed",
        link=feed_url,
        description=config.FEED_DESCRIPTION,
        language="en",
    )
    for post in posts:
        item_url = request.build_absolute_uri(post.get_absolute_url())
        rss.add_item(
            title=post.excerpt,
            link=item_url,
            description=post.content,
            pubdate=post.created_at,
            unique_id=item_url,
        )
    return HttpResponse(rss.writeString("utf-8"), content_type="application/rss+xml")


# ---------------------------------------------------------------------------
# CV
# ---------------------------------------------------------------------------


def _cv_meta():
    active = CVVersion.objects.filter(is_active=True).first()
    if active and active.file:
        try:
            return {
                "name": active.original_name or Path(active.file.name).name,
                "size": active.file.size,
                "updated": active.uploaded_at,
                "is_static": False,
            }
        except (OSError, ValueError):
            pass

    fallback = CV_STATIC_DIR / config.CV_FILENAME
    if fallback.exists():
        stat = fallback.stat()
        return {
            "name": config.CV_DISPLAY_NAME,
            "size": stat.st_size,
            "updated": datetime.fromtimestamp(
                stat.st_mtime, tz=timezone.get_current_timezone()
            ),
            "is_static": True,
        }
    return None


def _cv_source():
    active = CVVersion.objects.filter(is_active=True).first()
    if active and active.file:
        try:
            active.file.open("rb")
            return {
                "file": active.file,
                "name": active.original_name or Path(active.file.name).name,
            }
        except (OSError, ValueError):
            pass

    fallback = CV_STATIC_DIR / config.CV_FILENAME
    if fallback.exists():
        return {"file": open(fallback, "rb"), "name": config.CV_DISPLAY_NAME}
    return None


def cv_view(request):
    meta = _cv_meta()
    versions = CVVersion.objects.all() if request.user.is_staff else None
    return render(
        request,
        "portfolio/cv.html",
        {"cv": meta, "cv_exists": bool(meta), "versions": versions},
    )


@require_GET
def cv_file(request):
    source = _cv_source()
    if not source:
        raise Http404("No CV has been uploaded yet")
    response = FileResponse(source["file"], content_type="application/pdf")
    response["Content-Disposition"] = content_disposition_header(False, source["name"])
    response["X-Frame-Options"] = "SAMEORIGIN"
    return response


@require_GET
def cv_download(request):
    source = _cv_source()
    if not source:
        raise Http404("No CV has been uploaded yet")
    response = FileResponse(
        source["file"], as_attachment=True, filename=source["name"]
    )
    response["X-Frame-Options"] = "SAMEORIGIN"
    return response


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


def _login_key(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
    ip = forwarded or request.META.get("REMOTE_ADDR", "unknown")
    digest = hashlib.sha256(
        f"{ip}:{settings.SECRET_KEY}".encode("utf-8")
    ).hexdigest()[:16]
    return f"login:attempts:{digest}"


def _login_rate_limited(request):
    return (cache.get(_login_key(request)) or 0) >= LOGIN_ATTEMPT_LIMIT


def _record_login_attempt(request):
    key = _login_key(request)
    if cache.add(key, 1, timeout=LOGIN_ATTEMPT_WINDOW):
        return
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=LOGIN_ATTEMPT_WINDOW)


def _clear_login_attempts(request):
    cache.delete(_login_key(request))


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("portfolio:custom_admin")

    next_url = request.GET.get("next") or request.POST.get("next") or ""
    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":
        if _login_rate_limited(request):
            messages.error(
                request, "Too many attempts. Wait a few minutes and try again."
            )
        elif form.is_valid():
            user = form.get_user()
            if not user.is_staff:
                _record_login_attempt(request)
                messages.error(request, "This account does not have owner access.")
            else:
                auth_login(request, user)
                _clear_login_attempts(request)
                if next_url and url_has_allowed_host_and_scheme(
                    next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ):
                    return redirect(next_url)
                return redirect("portfolio:custom_admin")
        else:
            _record_login_attempt(request)
            messages.error(request, "Those credentials did not work.")

    return render(
        request,
        "portfolio/login.html",
        {"form": form, "next": next_url},
    )


@require_POST
def logout_view(request):
    auth_logout(request)
    messages.success(request, "Signed out.")
    return redirect("portfolio:home")


# ---------------------------------------------------------------------------
# Owner dashboard
# ---------------------------------------------------------------------------


@staff_required
def custom_admin_dashboard(request):
    today = timezone.localdate()
    window_start = today - timedelta(days=settings.ANALYTICS_WINDOW_DAYS - 1)

    today_views = (
        PageView.objects.filter(date=today).aggregate(total=Sum("views"))["total"] or 0
    )
    window_views = (
        PageView.objects.filter(date__gte=window_start).aggregate(
            total=Sum("views")
        )["total"]
        or 0
    )
    total_views = PageView.objects.aggregate(total=Sum("views"))["total"] or 0

    visitors_window = Visitor.objects.filter(
        last_seen__gte=timezone.now() - timedelta(days=settings.ANALYTICS_WINDOW_DAYS)
    ).count()
    returning_visitors = Visitor.objects.filter(views__gt=1).count()

    chart_start = today - timedelta(days=13)
    rows = (
        PageView.objects.filter(date__gte=chart_start)
        .values("date")
        .annotate(total=Sum("views"))
        .order_by("date")
    )
    by_date = {row["date"]: row["total"] for row in rows}
    chart = []
    for offset in range(14):
        day = chart_start + timedelta(days=offset)
        chart.append(
            {
                "date": day,
                "label": day.strftime("%d %b"),
                "views": by_date.get(day, 0),
            }
        )
    max_views = max((point["views"] for point in chart), default=0) or 1
    for point in chart:
        point["height"] = max(2, round((point["views"] / max_views) * 100))

    top_pages = list(
        PageView.objects.filter(date__gte=window_start)
        .values("path")
        .annotate(total=Sum("views"))
        .order_by("-total")[:8]
    )
    for page in top_pages:
        page["share"] = (
            round((page["total"] / window_views) * 100) if window_views else 0
        )

    context = {
        "today": today,
        "today_views": today_views,
        "window_views": window_views,
        "total_views": total_views,
        "visitors_window": visitors_window,
        "returning_visitors": returning_visitors,
        "posts_count": FeedPost.objects.count(),
        "cv_count": CVVersion.objects.count(),
        "chart": chart,
        "top_pages": top_pages,
        "recent_visitors": Visitor.objects.all()[:8],
        "recent_posts": FeedPost.objects.select_related("author")[:5],
        "pending": pending_snapshot(),
        "window_days": settings.ANALYTICS_WINDOW_DAYS,
    }
    return render(request, "portfolio/custom_admin/dashboard.html", context)


@staff_required
def custom_admin_visitors(request):
    query = (request.GET.get("q") or "").strip()
    visitors = Visitor.objects.all()
    if query:
        visitors = visitors.filter(
            Q(visitor_hash__icontains=query)
            | Q(last_path__icontains=query)
            | Q(referrer__icontains=query)
        )
    paginator = Paginator(visitors, 25)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "portfolio/custom_admin/visitors.html",
        {
            "page_obj": page_obj,
            "visitors": page_obj.object_list,
            "q": query,
            "total": visitors.count(),
        },
    )


def _csv_safe(value):
    text = str(value or "")
    if text.startswith(("=", "+", "-", "@")):
        return f"'{text}"
    return text


@staff_required
@require_GET
def custom_admin_visitors_export(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="visitors.csv"'
    writer = csv.writer(response)
    writer.writerow(
        [
            "visitor_hash",
            "views",
            "first_seen",
            "last_seen",
            "last_path",
            "referrer",
            "user_agent",
        ]
    )
    for visitor in Visitor.objects.all().iterator():
        writer.writerow(
            [
                visitor.visitor_hash,
                visitor.views,
                visitor.first_seen.isoformat(),
                visitor.last_seen.isoformat(),
                _csv_safe(visitor.last_path),
                _csv_safe(visitor.referrer),
                _csv_safe(visitor.user_agent),
            ]
        )
    return response


@staff_required
@require_POST
def custom_admin_visitor_delete(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    visitor.delete()
    messages.success(request, "Visitor record deleted.")
    return redirect("portfolio:custom_admin_visitors")


@staff_required
def custom_admin_posts(request):
    posts = FeedPost.objects.select_related("author").all()
    paginator = Paginator(posts, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "portfolio/custom_admin/posts.html",
        {"page_obj": page_obj, "posts": page_obj.object_list, "total": posts.count()},
    )


@staff_required
@require_http_methods(["GET", "POST"])
def custom_admin_cv(request):
    if request.method == "POST":
        form = CVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                CVVersion.objects.update(is_active=False)
                cv = form.save(commit=False)
                cv.uploaded_by = request.user
                cv.original_name = os.path.basename(
                    request.FILES["file"].name
                )[:255]
                cv.is_active = True
                cv.save()
            messages.success(request, "CV uploaded and set as the active version.")
            return redirect("portfolio:custom_admin_cv")
        messages.error(
            request, "The CV could not be uploaded. Check the file and try again."
        )
    else:
        form = CVUploadForm()

    versions = CVVersion.objects.all()
    return render(
        request,
        "portfolio/custom_admin/cv.html",
        {
            "form": form,
            "versions": versions,
            "active_cv": versions.filter(is_active=True).first(),
        },
    )


@staff_required
@require_POST
def custom_admin_cv_activate(request, pk):
    cv = get_object_or_404(CVVersion, pk=pk)
    cv.activate()
    messages.success(request, f"{cv.original_name} is now the active CV.")
    return redirect("portfolio:custom_admin_cv")


@staff_required
@require_POST
def custom_admin_cv_delete(request, pk):
    cv = get_object_or_404(CVVersion, pk=pk)
    was_active = cv.is_active
    name = cv.original_name
    cv.delete()

    if was_active:
        replacement = CVVersion.objects.first()
        if replacement:
            replacement.activate()

    messages.success(request, f"Deleted {name}.")
    return redirect("portfolio:custom_admin_cv")


# ---------------------------------------------------------------------------
# Analytics flush endpoint (called by an external 5-minute cron job)
# ---------------------------------------------------------------------------


@csrf_exempt
@require_POST
def analytics_flush(request):
    expected = settings.ANALYTICS_FLUSH_TOKEN
    if not expected:
        return JsonResponse(
            {"ok": False, "error": "flush_token_not_configured"}, status=503
        )

    supplied = request.headers.get("Authorization", "")
    if supplied.lower().startswith("bearer "):
        supplied = supplied[7:].strip()
    else:
        supplied = (
            request.POST.get("token")
            or request.headers.get("X-Analytics-Token")
            or ""
        ).strip()

    if not secrets.compare_digest(expected, supplied):
        return JsonResponse({"ok": False, "error": "unauthorized"}, status=403)

    try:
        result = flush()
    except Exception:
        return JsonResponse({"ok": False, "error": "flush_failed"}, status=500)

    status = 200 if result.get("ok") else 409
    return JsonResponse(result, status=status)


# ---------------------------------------------------------------------------
# SEO text files
# ---------------------------------------------------------------------------


@require_GET
def robots_txt(request):
    content = loader.render_to_string(
        "seo/robots.txt", {"domain": config.SITE_DOMAIN}
    )
    return HttpResponse(content, content_type="text/plain")


@require_GET
def llms_txt(request):
    latest_posts = FeedPost.objects.filter(is_published=True)[:10]
    content = loader.render_to_string(
        "seo/llms.txt",
        {"projects": PROJECTS, "latest_posts": latest_posts},
        request=request,
    )
    return HttpResponse(content, content_type="text/plain")

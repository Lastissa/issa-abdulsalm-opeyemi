import csv
import hashlib
import os
import secrets
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Sum
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.template.loader import render_to_string
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

from service_internal.caches import get_cache, set_cache, del_cache

from .analytics import flush_caches_count_to_db, pending_snapshot
from .content import get_page_content, get_site_payload
from .forms import CVUploadForm, FeedPostForm, LoginForm
from .http import (
    api_response,
    htmx_no_content,
    htmx_response,
    is_htmx,
    wants_json,
)
from .models import CVVersion, FeedPost, PageView, Project, Visitor

CV_STATIC_DIR = Path(settings.BASE_DIR) / "portfolio" / "static" / "portfolio" / "files"
CV_FALLBACK_FILENAME = "issa-abdulsalam-opeyemi-cv.pdf"
LOGIN_ATTEMPT_LIMIT = 10
LOGIN_ATTEMPT_WINDOW = 60 * 10


def staff_required(view):
    """private view that answers JSON and HTMX callers correctly."""

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and user.is_active and user.is_staff:
            return view(request, *args, **kwargs)

        login_url = reverse("portfolio:login")
        detail = "Sign in as the owner to continue."

        if wants_json(request):
            return api_response(
                "error", detail, http_status=401, redirect=login_url
            )
        if is_htmx(request):
            return htmx_response(
                "",
                toast={"status": "error", "detail": detail},
                redirect=login_url,
            )

        target = f"{login_url}?{urlencode({'next': request.get_full_path()})}"
        return redirect(target)

    return wrapper


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------


def home(request):
    published = Project.objects.filter(is_published=True).prefetch_related(
        "technologies"
    )
    featured = list(published.filter(featured=True)[:3])
    if not featured:
        featured = list(published[:3])

    latest_posts = FeedPost.objects.filter(is_published=True).select_related(
        "author"
    )[:4]

    return render(
        request,
        "portfolio/home.html",
        {
            "featured_projects": featured,
            "latest_posts": latest_posts,
        },
    )


def projects(request):
    items = Project.objects.filter(is_published=True).prefetch_related(
        "technologies"
    )
    return render(
        request,
        "portfolio/projects.html",
        {"projects": items, "page": get_page_content("projects")},
    )


def project_detail(request, slug):
    project = get_object_or_404(
        Project.objects.prefetch_related("technologies"),
        slug=slug,
        is_published=True,
    )
    related = (
        Project.objects.filter(is_published=True)
        .exclude(pk=project.pk)
        .prefetch_related("technologies")[:3]
    )
    return render(
        request,
        "portfolio/project_detail.html",
        {"project": project, "related_projects": related},
    )


def _feed_page(request, page_number=None):
    posts = FeedPost.objects.filter(is_published=True).select_related("author")
    paginator = Paginator(posts, 10)
    return paginator.get_page(page_number or request.GET.get("page"))


def _feed_context(request, form=None, page_number=None):
    page_obj = _feed_page(request, page_number)
    return {
        "page_obj": page_obj,
        "posts": page_obj.object_list,
        "form": form or FeedPostForm(),
        "post_count": FeedPost.objects.filter(is_published=True).count(),
        "page": get_page_content("feed"),
    }


def _feed_list_response(request, toast=None):
    """Replace the feed list and reset the composer after a mutation."""
    page_obj = _feed_page(request, 1)
    html = render_to_string(
        "portfolio/partials/feed_list.html",
        {
            "page_obj": page_obj,
            "posts": page_obj.object_list,
            "oob": True,
        },
        request=request,
    )
    html += render_to_string(
        "portfolio/partials/composer.html",
        {"form": FeedPostForm(), "oob": True},
        request=request,
    )
    return htmx_response(html, toast=toast)


def feed(request):
    if is_htmx(request) and request.GET.get("page"):
        page_obj = _feed_page(request)
        return render(
            request,
            "portfolio/partials/feed_append.html",
            {"page_obj": page_obj, "posts": page_obj.object_list},
        )
    return render(request, "portfolio/feed.html", _feed_context(request))


@staff_required
@require_POST
def feed_create(request):
    form = FeedPostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        if is_htmx(request):
            return _feed_list_response(
                request,
                toast={"status": "success", "detail": "Post published."},
            )
        messages.success(request, "Post published.")
        return redirect(post.get_absolute_url())

    if is_htmx(request):
        html = render_to_string(
            "portfolio/partials/composer.html",
            {"form": form, "oob": True},
            request=request,
        )
        return htmx_response(
            html,
            toast={
                "status": "error",
                "detail": "The post could not be published. Check the fields.",
            },
        )

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
            if is_htmx(request):
                return htmx_response(
                    "",
                    toast={"status": "success", "detail": "Post updated."},
                    redirect=post.get_absolute_url(),
                )
            return redirect(post.get_absolute_url())

        if is_htmx(request):
            html = render_to_string(
                "portfolio/partials/feed_edit_form.html",
                {"form": form, "post": post},
                request=request,
            )
            return htmx_response(
                html,
                toast={
                    "status": "error",
                    "detail": "The post could not be saved. Check the fields.",
                },
            )
        return render(
            request,
            "portfolio/feed_edit.html",
            {"form": form, "post": post},
            status=400,
        )

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
    if is_htmx(request):
        return _feed_list_response(
            request,
            toast={"status": "success", "detail": "Post deleted."},
        )
    messages.success(request, "Post deleted.")
    return redirect("portfolio:feed")


@require_GET
def feed_rss(request):
    site = get_site_payload()
    posts = FeedPost.objects.filter(is_published=True).select_related("author")[:50]
    feed_url = request.build_absolute_uri(reverse("portfolio:feed"))
    rss = Rss201rev2Feed(
        title=f"{site['full_name']} - Feed",
        link=feed_url,
        description=site["feed_description"],
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
    site = get_site_payload()
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

    fallback = CV_STATIC_DIR / CV_FALLBACK_FILENAME
    if fallback.exists():
        stat = fallback.stat()
        return {
            "name": site["cv_display_name"],
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

    fallback = CV_STATIC_DIR / CV_FALLBACK_FILENAME
    if fallback.exists():
        site = get_site_payload()
        return {"file": open(fallback, "rb"), "name": site["cv_display_name"]}
    return None


def cv_view(request):
    meta = _cv_meta()
    versions = CVVersion.objects.all() if request.user.is_staff else None
    return render(
        request,
        "portfolio/cv.html",
        {
            "cv": meta,
            "cv_exists": bool(meta),
            "versions": versions,
            "page": get_page_content("cv"),
        },
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
    return (get_cache(_login_key(request)) or 0) >= LOGIN_ATTEMPT_LIMIT


def _record_login_attempt(request):
    key = _login_key(request)
    current = get_cache(key)
    if not current:
        set_cache(key, 1, timeout=LOGIN_ATTEMPT_WINDOW)
        return
    try:
        set_cache(key, int(current) + 1, timeout=LOGIN_ATTEMPT_WINDOW)
    except (TypeError, ValueError):
        set_cache(key, 1, timeout=LOGIN_ATTEMPT_WINDOW)


def _clear_login_attempts(request):
    del_cache(_login_key(request))


def _safe_next(request, next_url):
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return ""


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        destination = reverse("portfolio:custom_admin")
        if wants_json(request):
            return api_response("ok", "Already signed in.", redirect=destination)
        return redirect(destination)

    next_url = request.GET.get("next") or request.POST.get("next") or ""
    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":
        if _login_rate_limited(request):
            detail = "Too many attempts. Wait a few minutes and try again."
            if wants_json(request):
                return api_response("error", detail, http_status=429)
            messages.error(request, detail)
        elif form.is_valid():
            user = form.get_user()
            if not user.is_staff:
                _record_login_attempt(request)
                detail = "This account does not have owner access."
                if wants_json(request):
                    return api_response("error", detail, http_status=403)
                messages.error(request, detail)
            else:
                auth_login(request, user)
                _clear_login_attempts(request)
                messages.success(request, "Signed in.")
                destination = _safe_next(request, next_url) or reverse(
                    "portfolio:custom_admin"
                )
                if wants_json(request):
                    return api_response("ok", "Signed in.", redirect=destination)
                return redirect(destination)
        else:
            _record_login_attempt(request)
            detail = "Invalid Credentials"
            if wants_json(request):
                return api_response("error", detail, http_status=400)
            messages.error(request, detail)

    return render(
        request,
        "portfolio/login.html",
        {
            "form": form,
            "next": next_url,
            "page": get_page_content("login"),
        },
    )


@require_POST
def logout_view(request):
    auth_logout(request)
    destination = reverse("portfolio:home")
    messages.success(request, "Signed out.")
    if wants_json(request):
        return api_response("ok", "Signed out.", redirect=destination)
    return redirect(destination)


# ---------------------------------------------------------------------------
# My dashboard
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
        "projects_count": Project.objects.count(),
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
    context = {
        "page_obj": page_obj,
        "visitors": page_obj.object_list,
        "q": query,
        "total": visitors.count(),
    }
    template = (
        "portfolio/custom_admin/partials/visitors_table.html"
        if is_htmx(request)
        else "portfolio/custom_admin/visitors.html"
    )
    return render(request, template, context)


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
    if is_htmx(request):
        return htmx_no_content(
            toast={"status": "success", "detail": "Visitor record deleted."}
        )
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
@require_POST
def custom_admin_post_delete(request, pk):
    post = get_object_or_404(FeedPost, pk=pk)
    post.delete()
    if is_htmx(request):
        return htmx_no_content(
            toast={"status": "success", "detail": "Post deleted."}
        )
    messages.success(request, "Post deleted.")
    return redirect("portfolio:custom_admin_posts")


def _cv_context(form=None):
    versions = CVVersion.objects.all()
    return {
        "form": form or CVUploadForm(),
        "versions": versions,
        "active_cv": versions.filter(is_active=True).first(),
    }


def _cv_oob_response(request, toast):
    context = _cv_context()
    html = render_to_string(
        "portfolio/custom_admin/partials/cv_upload.html",
        {"form": CVUploadForm(), "oob": True},
        request=request,
    )
    html += render_to_string(
        "portfolio/custom_admin/partials/cv_active.html",
        {**context, "oob": True},
        request=request,
    )
    html += render_to_string(
        "portfolio/custom_admin/partials/cv_versions.html",
        {**context, "oob": True},
        request=request,
    )
    return htmx_response(html, toast=toast)


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
            if is_htmx(request):
                return _cv_oob_response(
                    request,
                    {
                        "status": "success",
                        "detail": "CV uploaded and set as the active version.",
                    },
                )
            messages.success(request, "CV uploaded and set as the active version.")
            return redirect("portfolio:custom_admin_cv")

        if is_htmx(request):
            html = render_to_string(
                "portfolio/custom_admin/partials/cv_upload.html",
                {"form": form, "oob": True},
                request=request,
            )
            return htmx_response(
                html,
                toast={
                    "status": "error",
                    "detail": "The CV could not be uploaded. Check the file.",
                },
            )
        messages.error(
            request, "The CV could not be uploaded. Check the file and try again."
        )
    else:
        form = CVUploadForm()

    return render(
        request,
        "portfolio/custom_admin/cv.html",
        _cv_context(form=form),
    )


@staff_required
@require_POST
def custom_admin_cv_activate(request, pk):
    cv = get_object_or_404(CVVersion, pk=pk)
    cv.activate()
    if is_htmx(request):
        return _cv_oob_response(
            request,
            {
                "status": "success",
                "detail": f"{cv.original_name} is now the active CV.",
            },
        )
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

    if is_htmx(request):
        return _cv_oob_response(
            request,
            {"status": "success", "detail": f"Deleted {name}."},
        )
    messages.success(request, f"Deleted {name}.")
    return redirect("portfolio:custom_admin_cv")


# ---------------------------------------------------------------------------
# Analytics flush endpoint (called by an external 5-minute cron job)
# ---------------------------------------------------------------------------


@csrf_exempt
@require_POST
def analytics_flush(request):
    expected = getattr(settings, "SY_SECRET", "")
    if not expected:
        return api_response(
            "error",
            "The analytics flush token is not configured.",
            http_status=503,
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
        return api_response("error", "Unauthorized.", http_status=403)

    try:
        result = flush_caches_count_to_dbs()
    except Exception:
        return api_response("error", "Analytics flush failed.", http_status=500)

    if not result.get("ok"):
        return api_response(
            "error",
            "A flush is already running.",
            http_status=409,
            result=result,
        )

    return api_response(
        "ok",
        f"Flushed {result.get('views', 0)} views.",
        result=result,
        ok=True,
    )


# ---------------------------------------------------------------------------
# SEO text files
# ---------------------------------------------------------------------------


@require_GET
def robots_txt(request):
    domain = get_site_payload()["domain"] or request.build_absolute_uri("/")[:-1]
    content = loader.render_to_string(
        "seo/robots.txt", {"domain": domain.rstrip("/")}
    )
    return HttpResponse(content, content_type="text/plain")


@require_GET
def llms_txt(request):
    latest_posts = FeedPost.objects.filter(is_published=True)[:10]
    projects = Project.objects.filter(is_published=True).prefetch_related(
        "technologies"
    )
    content = loader.render_to_string(
        "seo/llms.txt",
        {"projects": projects, "latest_posts": latest_posts},
        request=request,
    )
    return HttpResponse(content, content_type="text/plain")

"""
portfolio/views.py

Deliberately plain function-based views. There is no database-backed
content on this site (see workflow.md, decision P1), so class-based
generic views (ListView, DetailView) would add structure without
adding value -- a clear case of the "don't over-engineer" instruction.
"""

from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views.decorators.http import require_GET

from .data import PROJECTS

CV_DIR = Path(settings.BASE_DIR) / "portfolio" / "static" / "portfolio" / "files"


def landing(request):
    """Landing page: about, education, skills, entry point to CV & projects."""
    return render(request, "portfolio/landing.html")


def projects(request):
    """Single page listing every project in full: summary, stack, links."""
    return render(request, "portfolio/projects.html", {"projects": PROJECTS})


def cv_view(request):
    """
    SEO/GEO-indexable page that embeds the CV inline (via <iframe>) so
    its content is viewable without forcing a download. Falls back to
    a friendly message if the PDF hasn't been placed yet -- see the
    README in portfolio/static/portfolio/files/.
    """
    cv_path = CV_DIR / _cv_filename()
    cv_exists = cv_path.exists()
    return render(
        request,
        "portfolio/cv.html",
        {"cv_exists": cv_exists},
    )


def cv_download(request):
    """Serves the CV PDF as a forced download with a clean filename."""
    from utility import config

    cv_path = CV_DIR / config.CV_FILENAME
    if not cv_path.exists():
        raise Http404(
            "CV file not found. Place your PDF at "
            "portfolio/static/portfolio/files/%s" % config.CV_FILENAME
        )
    return FileResponse(
        open(cv_path, "rb"),
        as_attachment=True,
        filename=config.CV_DISPLAY_NAME,
    )


def _cv_filename():
    from utility import config

    return config.CV_FILENAME


@require_GET
def robots_txt(request):
    """Plain-text robots.txt pointing crawlers at the sitemap."""
    content = loader.render_to_string(
        "seo/robots.txt", {"domain": request.build_absolute_uri("/")[:-1]}
    )
    return HttpResponse(content, content_type="text/plain")


@require_GET
def llms_txt(request):
    """
    llms.txt -- an emerging convention giving AI/LLM crawlers a clean,
    structured summary of the site (GEO: Generative Engine Optimization).
    See workflow.md, decision S2.
    """
    content = loader.render_to_string(
        "seo/llms.txt", {"projects": PROJECTS}, request=request
    )
    return HttpResponse(content, content_type="text/plain")

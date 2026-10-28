"""Small helpers for JSON and HTMX responses."""

import json

from django.http import HttpResponse, JsonResponse


def api_response(status="ok", detail="", http_status=None, **extra):
    """Every JSON endpoint returns at least ``status`` and ``detail``."""
    payload = {"status": status, "detail": detail}
    payload.update(extra)
    if http_status is None:
        http_status = 200 if status == "ok" else 400
    return JsonResponse(payload, status=http_status)


def wants_json(request):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return True
    return "application/json" in request.headers.get("Accept", "")


def is_htmx(request):
    return request.headers.get("HX-Request") == "true"


def htmx_response(html="", toast=None, status=200, redirect=None):
    response = HttpResponse(html, status=status)
    triggers = {}
    if toast:
        triggers["toast"] = toast
    if triggers:
        response["HX-Trigger"] = json.dumps(triggers)
    if redirect:
        response["HX-Redirect"] = redirect
    return response


def htmx_no_content(toast=None, redirect=None):
    # A 200 with an empty body lets hx-swap="delete" remove a row; 204 would
    # skip the swap entirely in HTMX.
    return htmx_response("", toast=toast, status=200, redirect=redirect)

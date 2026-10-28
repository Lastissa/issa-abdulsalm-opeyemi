from portfolio.content import get_site_payload


def site_context(request):
    """Expose database-backed site content to every template."""
    site = get_site_payload()

    canonical_url = ""
    avatar = site.get("avatar") or ""
    if request is not None:
        try:
            canonical_url = request.build_absolute_uri(request.path)
            if avatar.startswith("/"):
                avatar = request.build_absolute_uri(avatar)
        except Exception:
            canonical_url = ""

    site = {**site, "canonical_url": canonical_url, "avatar": avatar}
    return {"site": site}

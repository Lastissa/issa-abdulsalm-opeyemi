from . import config


def site_context(request):
    """Expose site-wide identity, SEO, and social data to all templates."""
    canonical_url = ""
    if request is not None:
        try:
            canonical_url = request.build_absolute_uri(request.path)
        except Exception:
            canonical_url = ""

    return {
        "site": {
            "full_name": config.FULL_NAME,
            "short_name": config.SHORT_NAME,
            "title": config.SITE_TITLE,
            "role_title": config.ROLE_TITLE,
            "location": config.LOCATION,
            "tagline": config.TAGLINE,
            "domain": config.SITE_DOMAIN,
            "default_description": config.DEFAULT_META_DESCRIPTION,
            "feed_description": config.FEED_DESCRIPTION,
            "socials": config.SOCIAL_LINKS,
            "education": config.EDUCATION,
            "skills": config.SKILLS,
            "cv_filename": config.CV_FILENAME,
            "cv_display_name": config.CV_DISPLAY_NAME,
            "canonical_url": canonical_url,
        }
    }

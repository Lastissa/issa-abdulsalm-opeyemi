from . import config


def site_context(request):
    """Expose site-wide identity/SEO/social data to all templates."""
    return {
        "site": {
            "full_name": config.FULL_NAME,
            "short_name": config.SHORT_NAME,
            "title": config.SITE_TITLE,
            "role_title": config.ROLE_TITLE,
            "tagline": config.TAGLINE,
            "domain": config.SITE_DOMAIN,
            "default_description": config.DEFAULT_META_DESCRIPTION,
            "default_keywords": ", ".join(config.DEFAULT_META_KEYWORDS),
            "socials": config.SOCIAL_LINKS,
            "education": config.EDUCATION,
            "skills": config.SKILLS,
            "cv_filename": config.CV_FILENAME,
            "cv_display_name": config.CV_DISPLAY_NAME,
        }
    }

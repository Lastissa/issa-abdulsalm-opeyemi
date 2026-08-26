"""
utility/context_processors.py

Registered in P_FOLIO/settings.py under TEMPLATES -> OPTIONS -> context_processors.
Makes site-wide config (utility/config.py) available in EVERY template as
`{{ site }}`, without every view having to pass it manually.

See workflow.md, decision U1, for why this lives in its own app-less
"utility" package instead of inside the portfolio app.
"""

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

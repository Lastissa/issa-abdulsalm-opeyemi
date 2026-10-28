"""Database-backed site content with a small cache in front of it."""

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.templatetags.static import static

from service_internal.caches import get_cache, set_cache, del_cache

from . import defaults
from .models import (
    EducationEntry,
    FeedPost,
    LoginPoint,
    NowItem,
    PageContent,
    Principle,
    Project,
    ProjectTechnology,
    SiteSettings,
    Skill,
    SkillGroup,
    SocialLink,
)

SITE_CACHE_KEY = "portfolio:site-payload:v2"
SITE_CACHE_TIMEOUT = 60 * 10


def _build_site_payload():
    site = SiteSettings.load()
    links = list(SocialLink.objects.filter(is_active=True))
    groups = list(
        SkillGroup.objects.filter(is_active=True).prefetch_related("skills")
    )
    education = list(EducationEntry.objects.filter(is_active=True))
    principles = list(Principle.objects.filter(is_active=True))
    now_items = list(NowItem.objects.filter(is_active=True))
    login_points = list(LoginPoint.objects.filter(is_active=True))
    projects = list(
        Project.objects.filter(is_published=True).prefetch_related("technologies")
    )

    skills = {}
    skill_groups = []
    for group in groups:
        items = [skill.name for skill in group.skills.all() if skill.is_active]
        if not items:
            continue
        skills[group.name] = items
        skill_groups.append({"name": group.name, "items": items})

    flat_skills = []
    for items in skills.values():
        for item in items:
            if item not in flat_skills:
                flat_skills.append(item)

    socials = {link.platform: link.url for link in links}
    socials["email"] = site.email

    technologies = {
        tech.name
        for project in projects
        for tech in project.technologies.all()
    }

    return {
        "full_name": site.full_name,
        "short_name": site.short_name,
        "initials": site.initials,
        "title": site.site_title or site.full_name,
        "role_title": site.role_title,
        "location": site.location,
        "city": site.city,
        "country_code": site.country_code,
        "tagline": site.tagline,
        "availability": site.availability,
        "email": site.email,
        "email_href": f"mailto:{site.email}" if site.email else "",
        "domain": getattr(settings, "FULL_DOMAIN", "").rstrip("/"),
        "default_description": site.default_meta_description,
        "feed_description": site.feed_description,
        "keywords": site.keywords,
        "hero_eyebrow": site.hero_eyebrow,
        "hero_heading": site.hero_heading,
        "hero_accent": site.hero_accent,
        "hero_lead": site.hero_lead,
        "focus_summary": site.focus_summary,
        "stack_summary": site.stack_summary,
        "years_experience": site.years_experience,
        "projects_delivered": site.projects_delivered or len(projects),
        "project_count": len(projects),
        "post_count": FeedPost.objects.filter(is_published=True).count(),
        "tech_count": len(technologies),
        "about_heading": site.about_heading,
        "about_body": site.about_body,
        "contact_heading": site.contact_heading,
        "contact_body": site.contact_body,
        "footer_note": site.footer_note,
        "avatar": site.avatar_url or static("portfolio/images/profile.jpg"),
        "cv_display_name": site.cv_display_name,
        "toast_position": site.toast_position,
        "default_theme": site.default_theme,
        "socials": socials,
        "social_links": [
            {
                "platform": link.platform,
                "label": link.label,
                "url": link.url,
                "handle": link.handle,
            }
            for link in links
        ],
        "skills": skills,
        "skill_groups": skill_groups,
        "flat_skills": flat_skills,
        "education": [
            {
                "institution": entry.institution,
                "credential": entry.credential,
                "status": entry.status,
                "period": entry.period,
            }
            for entry in education
        ],
        "principles": [
            {"title": principle.title, "body": principle.body}
            for principle in principles
        ],
        "now_items": [item.text for item in now_items],
        "login_points": [
            {"icon": point.icon, "text": point.text} for point in login_points
        ],
    }


def get_site_payload():
    payload = get_cache(SITE_CACHE_KEY)
    if not payload:
        payload = _build_site_payload()
        set_cache(SITE_CACHE_KEY, payload, SITE_CACHE_TIMEOUT)
    return payload


def get_page_content(key):
    """Return editable page copy, falling back to the seed values."""
    page = PageContent.objects.filter(key=key, is_active=True).first()
    if page is not None:
        return page
    values = defaults.PAGE_CONTENT.get(key, {})
    return PageContent(key=key, **values)


def invalidate_site_cache(**kwargs):
    del_cache(SITE_CACHE_KEY)


for _model in (
    SiteSettings,
    PageContent,
    SocialLink,
    SkillGroup,
    Skill,
    EducationEntry,
    Principle,
    NowItem,
    LoginPoint,
    Project,
    ProjectTechnology,
    FeedPost,
):
    post_save.connect(
        invalidate_site_cache,
        sender=_model,
        dispatch_uid=f"portfolio.invalidate.{_model.__name__}.save",
    )
    post_delete.connect(
        invalidate_site_cache,
        sender=_model,
        dispatch_uid=f"portfolio.invalidate.{_model.__name__}.delete",
    )

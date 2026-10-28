"""Idempotent seeding of the editable content tables.

Run automatically after ``migrate`` and available as
``python manage.py seed_content``. Existing rows are never overwritten.
"""

from django.db import transaction

from . import defaults

MODEL_NAMES = (
    "SiteSettings",
    "PageContent",
    "SocialLink",
    "SkillGroup",
    "Skill",
    "EducationEntry",
    "Principle",
    "NowItem",
    "LoginPoint",
    "Project",
    "ProjectTechnology",
)


def _resolve_models(apps):
    if apps is not None:
        return {name: apps.get_model("portfolio", name) for name in MODEL_NAMES}

    from . import models

    return {name: getattr(models, name) for name in MODEL_NAMES}


def seed_content(apps=None, using="default", verbosity=0):
    """Create any missing content rows without touching existing ones."""
    models = _resolve_models(apps)
    SiteSettings = models["SiteSettings"]
    PageContent = models["PageContent"]
    SocialLink = models["SocialLink"]
    SkillGroup = models["SkillGroup"]
    Skill = models["Skill"]
    EducationEntry = models["EducationEntry"]
    Principle = models["Principle"]
    NowItem = models["NowItem"]
    LoginPoint = models["LoginPoint"]
    Project = models["Project"]
    ProjectTechnology = models["ProjectTechnology"]

    created = 0

    with transaction.atomic(using=using):
        _, made = SiteSettings.objects.using(using).get_or_create(
            pk=1, defaults=defaults.SITE
        )
        created += int(made)

        for key, values in defaults.PAGE_CONTENT.items():
            _, made = PageContent.objects.using(using).get_or_create(
                key=key, defaults=values
            )
            created += int(made)

        for link in defaults.SOCIAL_LINKS:
            _, made = SocialLink.objects.using(using).get_or_create(
                platform=link["platform"], defaults=link
            )
            created += int(made)

        for group in defaults.SKILL_GROUPS:
            group_obj, made = SkillGroup.objects.using(using).get_or_create(
                name=group["name"],
                defaults={"order": group["order"]},
            )
            created += int(made)
            for index, name in enumerate(group["skills"]):
                _, made = Skill.objects.using(using).get_or_create(
                    group=group_obj,
                    name=name,
                    defaults={"order": index},
                )
                created += int(made)

        for entry in defaults.EDUCATION:
            _, made = EducationEntry.objects.using(using).get_or_create(
                institution=entry["institution"],
                credential=entry["credential"],
                defaults=entry,
            )
            created += int(made)

        for principle in defaults.PRINCIPLES:
            _, made = Principle.objects.using(using).get_or_create(
                title=principle["title"], defaults=principle
            )
            created += int(made)

        for item in defaults.NOW_ITEMS:
            _, made = NowItem.objects.using(using).get_or_create(
                text=item["text"], defaults=item
            )
            created += int(made)

        for point in defaults.LOGIN_POINTS:
            _, made = LoginPoint.objects.using(using).get_or_create(
                text=point["text"], defaults=point
            )
            created += int(made)

        for project in defaults.PROJECTS:
            data = {key: value for key, value in project.items() if key != "stack"}
            project_obj, made = Project.objects.using(using).get_or_create(
                slug=project["slug"], defaults=data
            )
            created += int(made)
            for index, tech in enumerate(project["stack"]):
                _, made = ProjectTechnology.objects.using(using).get_or_create(
                    project=project_obj,
                    name=tech,
                    defaults={"order": index},
                )
                created += int(made)

    if verbosity:
        print(f"Seeded {created} content row(s).")

    return created

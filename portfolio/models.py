import os
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models, transaction
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone


def cv_upload_to(instance, filename):
    """Store CVs under an opaque name so replacements never collide."""
    extension = os.path.splitext(filename)[1].lower() or ".pdf"
    return f"cv/{uuid.uuid4().hex}{extension}"


class FeedPost(models.Model):
    """A short update published on the public feed."""

    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="feed_posts",)
    content = models.TextField()
    image_url = models.URLField(max_length=500,blank=True,help_text="Optional external image URL.",
    )
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["-created_at"], name="feed_created_idx")]

    def __str__(self):
        return self.excerpt

    @property
    def excerpt(self):
        text = " ".join(self.content.split())
        return f"{text[:140]}..." if len(text) > 140 else text

    @property
    def was_edited(self):
        return (self.updated_at - self.created_at).total_seconds() > 60

    def get_absolute_url(self):
        return f"{reverse('portfolio:feed')}#post-{self.pk}"


class CVVersion(models.Model):
    """Every uploaded CV is kept until i deletes it."""

    file = models.FileField(upload_to=cv_upload_to)
    original_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="cv_uploads",)
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-uploaded_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"],
                condition=Q(is_active=True),
                name="one_active_cv_version",
            )
        ]

    def __str__(self):
        state = "active" if self.is_active else "archived"
        return f"{self.original_name} ({state})"

    @property
    def size_display(self):
        try:
            size = self.file.size
        except (OSError, ValueError):
            return "Unknown size"
        if size >= 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        return f"{max(1, size // 1024)} KB"

    def activate(self):
        with transaction.atomic():
            CVVersion.objects.exclude(pk=self.pk).update(is_active=False)
            if not self.is_active:
                self.is_active = True
                self.save(update_fields=["is_active"])
        return self


class PageView(models.Model):
    """Aggregated page views, written by the 5-minute cache flush."""

    path = models.CharField(max_length=255)
    date = models.DateField(db_index=True)
    views = models.PositiveBigIntegerField(default=0)

    class Meta:
        ordering = ["-date", "-views"]
        constraints = [
            models.UniqueConstraint(
                fields=["path", "date"],
                name="unique_pageview_path_date",
            )
        ]

    def __str__(self):
        return f"{self.path} - {self.date} ({self.views})"


class Visitor(models.Model):
    """Privacy-friendly visitor record. Only a salted hash is stored."""

    visitor_hash = models.CharField(max_length=64, unique=True)
    first_seen = models.DateTimeField()
    last_seen = models.DateTimeField(db_index=True)
    views = models.PositiveBigIntegerField(default=0)
    last_path = models.CharField(max_length=255, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    referrer = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-last_seen"]
        indexes = [models.Index(fields=["-last_seen"], name="visitor_seen_idx")]

    def __str__(self):
        return self.visitor_hash[:12]

    @property
    def is_returning(self):
        return self.views > 1

    @property
    def short_hash(self):
        return self.visitor_hash[:10]

    @property
    def seen_recently(self):
        return self.last_seen >= timezone.now() - timedelta(hours=24)


# ---------------------------------------------------------------------------
# Editable site content
#
# Everything the public site renders comes from these tables. The static
# modules in ``defaults.py`` are seed data only; they are never read while a
# page is being rendered.
# ---------------------------------------------------------------------------


class SiteSettings(models.Model):
    """Singleton row holding identity, SEO, hero, and contact copy."""

    TOAST_TOP = "top"
    TOAST_BOTTOM = "bottom"
    TOAST_CHOICES = [
        (TOAST_TOP, "Top right"),
        (TOAST_BOTTOM, "Bottom right"),
    ]

    THEME_SYSTEM = "system"
    THEME_LIGHT = "light"
    THEME_DARK = "dark"
    THEME_CHOICES = [
        (THEME_SYSTEM, "Follow the device"),
        (THEME_LIGHT, "Light"),
        (THEME_DARK, "Dark"),
    ]

    full_name = models.CharField(max_length=120, default="Issa Opeyemi")
    short_name = models.CharField(max_length=80, default="Opeyemi")
    initials = models.CharField(max_length=4, default="IA")
    role_title = models.CharField(max_length=120, default="Backend Developer")
    location = models.CharField(max_length=120, default="Ilorin, Nigeria")
    city = models.CharField(max_length=80, default="Ilorin")
    country_code = models.CharField(max_length=2, default="NG")
    tagline = models.CharField(
        max_length=200,
        default=(
            "I build maintainable systems and the interfaces that make them usable."
        ),
    )
    availability = models.CharField(
        max_length=120, default="Available for backend work"
    )
    email = models.EmailField(default="lastissa11@gmail.com")

    site_title = models.CharField(
        max_length=120, default="Issa Opeyemi"
    )
    default_meta_description = models.TextField(
        default=(
            "Issa Abdulsalam Opeyemi is a backend developer working with Django, "
            "Django REST Framework, PostgreSQL, Flutter, and Go. Explore projects, "
            "the build feed, and the CV."
        )
    )
    feed_description = models.TextField(
        default=(
            "Short updates on what I am building, learning, and shipping: Django, "
            "APIs, Flutter, Go, and the occasional hard-won lesson."
        )
    )
    keywords = models.CharField(
        max_length=300,
        default=(
            "Django, Django REST Framework, PostgreSQL, Python, Flutter, Go, "
            "Backend Developer"
        ),
        help_text="Comma-separated keywords for metadata.",
    )

    hero_eyebrow = models.CharField(max_length=120, default="Backend developer")
    hero_heading = models.CharField(
        max_length=200, default="I build backends that stay"
    )
    hero_accent = models.CharField(max_length=80, default="maintainable")
    hero_lead = models.TextField(
        default=(
            "I am Issa Abdulsalam Opeyemi. I work with Django, Django REST "
            "Framework, PostgreSQL, Flutter, and Go. Based in Ilorin, Nigeria."
        )
    )
    focus_summary = models.CharField(
        max_length=200,
        default="Backend systems, APIs, and data-heavy products",
    )
    stack_summary = models.CharField(
        max_length=200, default="Django, DRF, PostgreSQL, Flutter, Go"
    )
    years_experience = models.PositiveSmallIntegerField(default=3)
    projects_delivered = models.PositiveSmallIntegerField(default=7)

    about_heading = models.CharField(max_length=160, default="How I work")
    about_body = models.TextField(
        default=(
            "A product without findings is a product waiting to fail. I start by "
            "understanding the data, the constraints, and the failure cases, then "
            "choose the tool that fits the job."
        )
    )
    contact_heading = models.CharField(
        max_length=200, default="Have a backend problem worth solving?"
    )
    contact_body = models.TextField(
        default=(
            "Email is the fastest way to reach me. I also answer on WhatsApp and "
            "LinkedIn."
        )
    )
    footer_note = models.CharField(
        max_length=200,
        default="Django, DRF, PostgreSQL, and a bias for maintainable systems.",
    )

    avatar_url = models.URLField(
        blank=True,
        default="",
        help_text=(
            "Optional external portrait URL. Leave blank to use the bundled photo."
        ),
    )
    cv_display_name = models.CharField(
        max_length=160, default="Issa Abdulsalam Opeyemi - CV.pdf"
    )

    toast_position = models.CharField(
        max_length=10,
        choices=TOAST_CHOICES,
        default=TOAST_TOP,
        help_text="Where Django messages appear as toasts.",
    )
    default_theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default=THEME_SYSTEM,
        help_text="Theme used before a visitor picks one.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        instance, _ = cls.objects.get_or_create(pk=1)
        return instance


class PageContent(models.Model):
    """Editable hero copy and metadata for each public page."""

    KEY_CHOICES = [
        ("projects", "Projects"),
        ("feed", "Feed"),
        ("cv", "CV"),
        ("login", "Login"),
    ]

    key = models.CharField(max_length=32, unique=True, choices=KEY_CHOICES)
    eyebrow = models.CharField(max_length=120, blank=True)
    heading = models.CharField(max_length=200, blank=True)
    intro = models.TextField(blank=True)
    meta_description = models.TextField(blank=True)
    og_description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["key"]
        verbose_name = "Page content"
        verbose_name_plural = "Page content"

    def __str__(self):
        return self.get_key_display()


class SocialLink(models.Model):
    """Ordered social/contact links rendered in the footer and CTA."""

    PLATFORM_CHOICES = [
        ("github", "GitHub"),
        ("linkedin", "LinkedIn"),
        ("twitter", "X / Twitter"),
        ("whatsapp", "WhatsApp"),
        ("website", "Website"),
        ("email", "Email"),
    ]

    platform = models.CharField(
        max_length=20, unique=True, choices=PLATFORM_CHOICES
    )
    label = models.CharField(max_length=60)
    url = models.CharField(
        max_length=300,
        help_text="Full URL. For email use a mailto: address.",
    )
    handle = models.CharField(max_length=120, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "platform"]

    def __str__(self):
        return self.label


class SkillGroup(models.Model):
    """A named group of technologies shown on the landing page and CV."""

    name = models.CharField(max_length=80, unique=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Skill(models.Model):
    group = models.ForeignKey(
        SkillGroup, on_delete=models.CASCADE, related_name="skills"
    )
    name = models.CharField(max_length=120)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["group", "name"], name="unique_skill_per_group"
            )
        ]

    def __str__(self):
        return f"{self.group.name}: {self.name}"


class EducationEntry(models.Model):
    institution = models.CharField(max_length=200)
    credential = models.CharField(max_length=200)
    status = models.CharField(max_length=80, blank=True)
    period = models.CharField(max_length=80, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "credential"]
        verbose_name = "Education entry"
        verbose_name_plural = "Education entries"

    def __str__(self):
        return f"{self.credential} - {self.institution}"


class Principle(models.Model):
    """A "how I work" card on the landing page."""

    title = models.CharField(max_length=160)
    body = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title


class NowItem(models.Model):
    """A single line in the "right now" card."""

    text = models.CharField(max_length=240)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "text"]
        verbose_name = "Right now item"
        verbose_name_plural = "Right now items"

    def __str__(self):
        return self.text


class LoginPoint(models.Model):
    """A benefit line on the owner login page."""

    ICON_CHOICES = [
        ("cv", "CV"),
        ("feed", "Feed"),
        ("analytics", "Analytics"),
    ]

    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default="feed")
    text = models.CharField(max_length=240)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "text"]
        verbose_name = "Login point"
        verbose_name_plural = "Login points"

    def __str__(self):
        return self.text


class Project(models.Model):
    """A case study rendered on the projects index and detail page."""

    STATUS_CHOICES = [
        ("live", "Live"),
        ("progress", "In progress"),
        ("sale", "For sale"),
        ("functional", "Functional"),
        ("completed", "Completed"),
        ("maintained", "Actively maintained"),
    ]

    slug = models.SlugField(max_length=120, unique=True)
    name = models.CharField(max_length=160)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="live"
    )
    summary = models.TextField()
    description = models.TextField()
    focus = models.TextField(
        blank=True,
        default="",
        help_text="What you focused on for this build.",
    )
    role = models.CharField(max_length=120, blank=True)
    year = models.CharField(max_length=20, blank=True)
    project_type = models.CharField(
        max_length=80,
        blank=True,
        default="Web application",
    )
    live_url = models.URLField(max_length=300, blank=True)
    live_label = models.CharField(max_length=80, blank=True)
    repo_url = models.URLField(max_length=300, blank=True)
    embeddable = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    preview_note = models.TextField(
        blank=True,
        default="",
        help_text="Shown under the live preview frame.",
    )
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]
        indexes = [
            models.Index(fields=["is_published", "order"], name="project_public_idx")
        ]

    def __str__(self):
        return self.name

    @property
    def status_class(self):
        return self.status

    @property
    def status_label(self):
        return self.get_status_display()

    @property
    def stack(self):
        return [tech.name for tech in self.technologies.all()]

    @property
    def primary_stack(self):
        stack = self.stack
        return stack[0] if stack else ""

    def get_absolute_url(self):
        return reverse("portfolio:project_detail", args=[self.slug])


class ProjectTechnology(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="technologies"
    )
    name = models.CharField(max_length=80)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "name"], name="unique_tech_per_project"
            )
        ]
        verbose_name = "Project technology"
        verbose_name_plural = "Project technologies"

    def __str__(self):
        return f"{self.project.name}: {self.name}"


# Keep the DB row and the physical file in sync when a version is deleted.
from django.db.models.signals import post_delete  # noqa: E402
from django.dispatch import receiver  # noqa: E402


@receiver(post_delete, sender=CVVersion)
def delete_cv_file(sender, instance, **kwargs):
    if instance.file:
        try:
            instance.file.delete(save=False)
        except Exception:
            # File cleanup is best-effort and must not block the DB delete.
            pass

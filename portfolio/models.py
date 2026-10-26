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

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feed_posts",
    )
    content = models.TextField()
    image_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="Optional external image URL. Images are never uploaded here.",
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
    """Every uploaded CV is kept until the owner deletes it."""

    file = models.FileField(upload_to=cv_upload_to)
    original_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cv_uploads",
    )
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


# Keep the DB row and the physical file in sync when a version is deleted.
from django.db.models.signals import post_delete  # noqa: E402
from django.dispatch import receiver  # noqa: E402


@receiver(post_delete, sender=CVVersion)
def delete_cv_file(sender, instance, **kwargs):
    if instance.file:
        try:
            instance.file.delete(save=False)
        except OSError:
            pass

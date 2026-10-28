from django.apps import AppConfig
from django.db.models.signals import post_migrate


class PortfolioConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "portfolio"

    def ready(self):
        # Register cache invalidation and load the seed hook only once.
        from . import content  # noqa: F401

        post_migrate.connect(
            seed_after_migrate,
            sender=self,
            dispatch_uid="portfolio.seed_after_migrate",
        )


def seed_after_migrate(sender, app_config, using, **kwargs):
    """Populate the content tables when the app is migrated for the first time."""
    from django.db import DatabaseError

    from .seed import seed_content

    try:
        seed_content(apps=kwargs.get("apps"), using=using)
    except DatabaseError:
        # A partial migrate (for example, a squashed state) should not crash.
        return

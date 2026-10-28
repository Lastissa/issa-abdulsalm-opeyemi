from django.core.management.base import BaseCommand

from portfolio.seed import seed_content


class Command(BaseCommand):
    help = "Create any missing editable site content (idempotent)."

    def handle(self, *args, **options):
        created = seed_content(verbosity=1)
        self.stdout.write(
            self.style.SUCCESS(f"Content ready ({created} new row(s)).")
        )

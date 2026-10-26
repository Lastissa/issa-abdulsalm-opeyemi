from django.core.management.base import BaseCommand

from portfolio.analytics import flush


class Command(BaseCommand):
    help = "Flush cached page-view counters into the database."

    def handle(self, *args, **options):
        result = flush()
        if not result.get("ok"):
            self.stderr.write(
                self.style.WARNING(
                    f"Flush skipped: {result.get('error', 'unknown error')}"
                )
            )
            return
        self.stdout.write(
            self.style.SUCCESS(
                "Flushed "
                f"{result['views']} views across {result['page_rows']} page rows "
                f"and {result['visitor_rows']} visitor rows."
            )
        )

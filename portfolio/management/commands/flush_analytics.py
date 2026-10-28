from django.core.management.base import BaseCommand

from portfolio.analytics import flush_caches_count_to_db


class Command(BaseCommand):
    help = "send cached page-view counters into the database."

    def handle(self, *args, **options):
        result = flush_caches_count_to_db()
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

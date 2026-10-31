import datetime

from django.core.management.base import BaseCommand
from wagtail_headless_preview.models import PagePreview


class Command(BaseCommand):
    help = "Delete PagePreview rows older than the given number of days (default 1)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=1,
            help="Delete previews older than this many days (default: 1).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report how many rows would be deleted without deleting them.",
        )

    def handle(self, *args, **options):
        days = options["days"]
        dry_run = options["dry_run"]

        cutoff = datetime.date.today() - datetime.timedelta(days=days)
        queryset = PagePreview.objects.filter(created_at__lt=cutoff)
        count = queryset.count()

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"Would delete {count} PagePreview row(s) older than {days} "
                    f"day(s) (before {cutoff})."
                )
            )
            return

        deleted, _ = queryset.delete()
        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {deleted} PagePreview row(s) older than {days} "
                f"day(s) (before {cutoff})."
            )
        )

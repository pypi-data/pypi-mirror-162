"""Add IPs to the blocklist from a file."""
import datetime
import logging
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime

from ...models import DEFAULT_COOLDOWN, BlockedIP

logger = logging.getLogger(__name__)
DEFAULT_DAYS = settings.BLOCKLIST_CONFIG.get("cooldown") or DEFAULT_COOLDOWN


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true", help="Preview the resulting update rather than performing it"
        )
        parser.add_argument(
            "--cooldown", help="'cooldown' field value for the added IPs", default=DEFAULT_DAYS
        )
        parser.add_argument("--file", help="Path to file with whitespace-separated IPs", default="ips.txt")
        parser.add_argument("--reason", help="'reason' field value for the added IPs")
        parser.add_argument(
            "--replace", action="store_true", help="Update IPs already in the DB; otherwise, skip"
        )
        parser.add_argument(
            "--timestamp",
            help="Datetime (ISO-8601) for'first_seen' and 'last_seen'; otherwise current datetime will be used",
        )

    help = __doc__

    def handle(self, *args, **options):
        for option in "dry_run cooldown file reason replace timestamp verbosity".split():
            setattr(self, option, options.get(option))
        try:
            file_handle = open(self.file)
        except FileNotFoundError as e:
            sys.exit(f"Failed to open file: {e}")
        seen = parse_datetime(self.timestamp) if self.timestamp else datetime.datetime.now()
        ips = set(file_handle.read().split())
        total = len(ips)
        self.puts(f"Read {total} unique IPs from file")
        if not self.dry_run:
            self.puts("Saving to blocklist")
        else:
            self.puts("Dry run, not saving to database")
        counts = {"added": 0, "skipped": 0}
        for n, ip in enumerate(ips):
            if len(ips) > 100 and (n * 10) % (total // 10) == 0:
                self.puts(f"Processed {n} of {total}")
            if BlockedIP.objects.filter(ip=ip).exists() and not self.replace:
                self.puts(f"Skipping {ip} - already present")
                counts["skipped"] += 1
                continue
            if not self.dry_run:
                entry = BlockedIP.objects.create(ip=ip, first_seen=seen, cooldown=self.cooldown)
                if self.reason:
                    entry.reason = self.reason
                entry.save()
                counts["added"] += 1
        self.puts(f"Done. Added {counts['added']}, skipped {counts['skipped']}")

    def puts(self, text):
        if self.verbosity > 0:
            print(text)

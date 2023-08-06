"""Update specified IPs with new last-seen, reason, or cooldown."""
import logging

from django.core.management.base import BaseCommand

from ...models import BlockedIP

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("ips", nargs="+", type=str, help="IPs (space-separated) to update")
        parser.add_argument("--cooldown")
        parser.add_argument("--reason")
        parser.add_argument("--last-seen", help="Datetime in ISO8601 format")

    help = __doc__

    def handle(self, *args, **options):
        ips = options.get("ips")
        cooldown = options.get("cooldown")
        reason = options.get("reason")
        last_seen = options.get("last_seen")
        for ip in ips:
            try:
                entry = BlockedIP.objects.get(ip=ip)
            except BlockedIP.DoesNotExist:
                print(f"{ip} not found")
                continue
            else:
                if reason:
                    entry.reason = reason
                if cooldown:
                    entry.cooldown = cooldown
                if last_seen:
                    entry.last_seen = last_seen
                entry.save()
                print(f"Updated existing entry for {ip}")

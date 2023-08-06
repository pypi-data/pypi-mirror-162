"""Add IPs to blocklist."""
import datetime
import logging

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.core.validators import validate_ipv46_address

from ...models import BlockedIP
from ...utils import COOLDOWN

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("ips", nargs="+", type=str, help="IPs (space-separated) to add")
        parser.add_argument(
            "--cooldown",
            help=f"Days with no connections before IP is dropped from blocklist (default: {COOLDOWN})",
        )
        parser.add_argument("--reason", help="'reason' field value for the added IPs", default="")

    help = __doc__

    def handle(self, *args, **options):
        ips = options.get("ips")
        cooldown = options.get("cooldown")
        reason = options.get("reason")
        now = datetime.datetime.now()
        for ip in ips:
            try:
                validate_ipv46_address(ip)
            except ValidationError:
                print(f"Invalid IP: {ip}")
                continue
            entry, created = BlockedIP.objects.get_or_create(ip=ip)
            if created:
                entry.reason = reason
                entry.cooldown = cooldown or COOLDOWN
                entry.first_seen = now
                entry.save()
                print(f"Created entry for {ip}")
            else:
                print(f"{ip} already listed; use update_blocklist to update")

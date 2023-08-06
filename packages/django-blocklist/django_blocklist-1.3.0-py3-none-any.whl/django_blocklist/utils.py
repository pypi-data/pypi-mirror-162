import datetime
import logging

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest

from .models import DEFAULT_COOLDOWN, BlockedIP

logger = logging.getLogger(__name__)

CACHE_KEY = "django-blocklist-ips"
CACHE_TTL = settings.BLOCKLIST_CONFIG.get("cache-ttl", 60)
COOLDOWN = settings.BLOCKLIST_CONFIG.get("cooldown", DEFAULT_COOLDOWN)


def user_ip_from_request(request: HttpRequest) -> str:
    """Returns user's IP. If IP can't be determined, return empty string and log a warning."""
    keys = ["HTTP_X_REAL_IP", "REMOTE_ADDR"]
    for key in keys:
        if ip := request.META.get(key):
            return ip
    # `HTTP_X_FORWARDED_FOR` is a comma-separated list with originating IP first
    if forwarded := request.META.get("HTTP_X_FORWARDED_FOR"):
        return forwarded.split(",")[0]
    logger.warning("No IP address could be found on request: {}".format(request.META))
    return ""


def get_blocklist(force_cache: bool = False) -> set:
    """Read the blocklist from cache and return it as a set. Read from database if cache is expired or `force_cache` is True."""
    blocked_ips = cache.get(CACHE_KEY)
    if blocked_ips is None or force_cache is True:
        blocked_ips = set(o.ip for o in BlockedIP.objects.all())
        cache.set(CACHE_KEY, list(blocked_ips), CACHE_TTL)
        logger.info(f"Read {len(blocked_ips)} IPs from blocklist storage; cached.")
    return set(blocked_ips)


def add_to_blocklist(ips: set, reason="") -> None:
    """Add the provided IPs to the blocklist, with optional `reason`"""
    now = datetime.datetime.now()
    for ip in ips:
        entry, new = BlockedIP.objects.get_or_create(ip=ip)  # type: ignore
        entry.reason = reason
        entry.cooldown = COOLDOWN
        entry.last_seen = now
        entry.save()
        if not new:
            logger.info(f"add_to_blocklist: updated existing entry for IP {ip}")
    logger.info(f'Added to blocklist: {ips} -- "{reason}"')
    # Update cache
    get_blocklist(force_cache=True)


def remove_from_blocklist(ip: str) -> bool:
    """Remove the IP from the blocklist. Return True if successful, False if it wasn't found."""
    try:
        BlockedIP.objects.get(ip=ip).delete()
        return True
    except BlockedIP.DoesNotExist:
        logger.warning(f"Removal of {ip} requested, but not found in blocklist.")
        return False

import datetime
import logging

from django.conf import settings
from django.http import HttpResponseBadRequest

from .models import BlockedIP
from .utils import user_ip_from_request

logger = logging.getLogger(__name__)


def denial_template():
    return (
        settings.BLOCKLIST_CONFIG.get("denial-template")
        or "Your IP address {ip} has been blocked. Try again in {cooldown} days."
    )


class BlocklistMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if entry_qs := BlockedIP.objects.filter(ip=user_ip_from_request(request)):
            entry = entry_qs.get()
            logger.warning("{} request blocked from {}".format(request.method, entry.ip))
            entry.last_seen = datetime.datetime.now()
            entry.tally += 1
            entry.save()
            return HttpResponseBadRequest(denial_template().format(ip=entry.ip, cooldown=entry.cooldown))
        else:
            return self.get_response(request)

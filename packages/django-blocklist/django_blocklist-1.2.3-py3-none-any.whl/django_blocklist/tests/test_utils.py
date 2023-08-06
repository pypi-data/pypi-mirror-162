from django.core.cache import cache
from django.db.utils import IntegrityError
from django.http import HttpRequest
from django.test import TestCase

from ..utils import (
    CACHE_KEY,
    add_to_blocklist,
    get_blocklist,
    remove_from_blocklist,
    user_ip_from_request,
)


class UtilsTests(TestCase):
    def setUp(self):
        cache.delete(CACHE_KEY)

    def tearDown(self):
        cache.delete(CACHE_KEY)

    def test_get_list(self):
        cache.set(CACHE_KEY, ["1.1.1.1"])
        result = get_blocklist()
        self.assertEqual(result, {"1.1.1.1"})

    def test_add(self):
        ips = {"2.2.2.2", "3.3.3.3"}
        add_to_blocklist(ips, reason="whatever")
        result = get_blocklist()
        self.assertEqual(result, ips)

    def test_add_duplicate(self):
        ip = "9.9.9.9"
        add_to_blocklist(ip)
        try:
            add_to_blocklist(ip)
        except IntegrityError:
            self.fail("add_to_blocklist failed to handle duplicate IP")

    def test_remove(self):
        ip_as_list = ["1.1.1.1"]
        cache.set(CACHE_KEY, ip_as_list)
        assert get_blocklist() == set(ip_as_list)
        remove_from_blocklist(ip_as_list)
        self.assertEqual(get_blocklist(force_cache=True), set())

    def test_get_user_ip(self):
        request = HttpRequest()
        result = user_ip_from_request(request)
        self.assertEqual(result, "")
        ip = "4.4.4.4"
        for key in ["HTTP_X_REAL_IP", "REMOTE_ADDR"]:
            request.META[key] = ip
            self.assertEqual(user_ip_from_request(request), ip)
            del request.META[key]
        request.META["HTTP_X_FORWARDED_FOR"] = "5.5.5.5,6.6.6.6"
        result = user_ip_from_request(request)
        self.assertEqual(result, "5.5.5.5")

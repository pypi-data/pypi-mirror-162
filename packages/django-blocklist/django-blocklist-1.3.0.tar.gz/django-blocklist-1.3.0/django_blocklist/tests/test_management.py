import datetime
import pytest
import sys
import unittest
from django.core.management import call_command
from io import StringIO

from ..models import BlockedIP


@pytest.mark.django_db
class CommandsTest(unittest.TestCase):
    def setUp(self):
        BlockedIP.objects.all().delete()

    def tearDown(self):
        BlockedIP.objects.all().delete()

    def test_clean(self):
        two_days_ago = datetime.datetime.now() - datetime.timedelta(days=2)
        BlockedIP.objects.create(ip="1.1.1.1", cooldown=1, last_seen=two_days_ago)
        BlockedIP.objects.create(ip="2.2.2.2", cooldown=3, last_seen=two_days_ago)
        # We now have two IPs
        assert BlockedIP.objects.count() == 2
        # Running clean_blocklist with --dry-run doesn't delete one
        call_command("clean_blocklist", verbosity=0, dry_run=1)
        self.assertEqual(BlockedIP.objects.count(), 2)
        # Running clean_blocklist does delete one
        call_command("clean_blocklist", verbosity=0)
        self.assertEqual(BlockedIP.objects.count(), 1)
        # The one that should still be there, is still there
        self.assertTrue(BlockedIP.objects.filter(ip="2.2.2.2").exists())

    def test_add(self):
        call_command("update_blocklist", "3.3.3.3", verbosity=0)
        self.assertTrue(BlockedIP.objects.filter(ip="3.3.3.3").exists())

    def test_remove(self):
        BlockedIP.objects.create(ip="4.4.4.4")
        call_command("remove_from_blocklist", "4.4.4.4", verbosity=0)
        self.assertEqual(BlockedIP.objects.filter(ip="4.4.4.4").count(), 0)

    def test_add_invalid(self):
        out = StringIO()
        sys.stdout = out
        bad_ip = "foo"
        call_command("update_blocklist", bad_ip, verbosity=0)
        self.assertIn("Invalid", out.getvalue())

    def test_update(self):
        BlockedIP.objects.create(ip="5.5.5.5", reason="R1", cooldown=1)
        call_command("update_blocklist", "5.5.5.5", reason="R2", cooldown=2)
        entry = BlockedIP.objects.get(ip="5.5.5.5")
        self.assertEqual(entry.reason, "R2")
        self.assertEqual(entry.cooldown, 2)

    def test_report(self):
        out = StringIO()
        sys.stdout = out
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)
        BlockedIP.objects.create(ip="7.7.7.7", first_seen=yesterday, last_seen=today)
        call_command("report_blocklist")
        result = out.getvalue()
        self.assertIn("7.7.7.7 -- 0 blocks", result)

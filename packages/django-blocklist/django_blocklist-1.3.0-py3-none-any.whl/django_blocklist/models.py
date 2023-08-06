import datetime

from django.contrib.humanize.templatetags.humanize import intcomma, naturaltime
from django.db import models
from django.db.models.fields import CharField, DateTimeField, GenericIPAddressField, IntegerField
from django.utils import timezone

DEFAULT_COOLDOWN = 7


class BlockedIP(models.Model):
    ip = GenericIPAddressField(primary_key=True, verbose_name="IP")
    first_seen = DateTimeField(default=timezone.now, db_index=True)
    last_seen = DateTimeField(blank=True, null=True, db_index=True)
    cooldown = IntegerField(
        default=DEFAULT_COOLDOWN,
        help_text="Cooldown period; number of days with no connections before IP is dropped from blocklist",
    )
    reason = CharField(blank=True, max_length=255, default="", db_index=True)
    tally = IntegerField(default=0, help_text="Number of times this IP has been blocked since first_seen")

    class Meta:
        get_latest_by = "first_seen"
        ordering = ["-last_seen", "ip"]
        verbose_name = "blocked IP"

    def __str__(self) -> str:
        return self.ip

    def verbose_str(self):
        timespan = naturaltime(self.first_seen).replace(" ago", "")
        return (
            f"{self.ip}"
            + f" -- {intcomma(self.tally)} blocks in {timespan}"
            + f" -- seen {naturaltime(self.last_seen)}"
            + f" -- {self.cooldown} day cooldown"
            + f"{' -- ' + self.reason if self.reason else ''}"
        )

    def has_expired(self):
        """Has the IP cooled long enough to be removed from the list?"""
        quiet_time = datetime.datetime.now() - self.last_seen
        return quiet_time.days >= self.cooldown

    def save(self, *args, **kwargs):
        if self.last_seen is None:
            self.last_seen = self.first_seen
        super().save(*args, **kwargs)

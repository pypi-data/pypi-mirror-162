from django.contrib import admin
from django.http import HttpResponseRedirect

from .models import BlockedIP


@admin.display(description="Reason")
def reason_truncated(entry):
    return entry.reason[:20] + ("..." if len(entry.reason) > 20 else "")


@admin.display(description="Cooldown")
def cooldown(entry):
    return f"{entry.cooldown} days"


@admin.action(permissions=["view"])
def look_up_first_selected_IP(modeladmin, request, queryset):
    obj = queryset[0]
    return HttpResponseRedirect(f"https://whatismyipaddress.com/ip/{obj.ip}")


class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ["ip", "first_seen", "last_seen", "tally", cooldown, reason_truncated]
    list_filter = ["first_seen", "last_seen", "cooldown", "reason"]
    search_fields = ["ip", "reason"]
    actions = [look_up_first_selected_IP]

    class Meta:
        model = BlockedIP


admin.site.register(BlockedIP, BlockedIPAdmin)

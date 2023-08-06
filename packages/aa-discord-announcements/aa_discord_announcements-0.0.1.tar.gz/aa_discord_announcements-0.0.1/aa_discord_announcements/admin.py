"""
Settings for the admin backend
"""

# Django
from django.contrib import admin

# AA Discord Announcements
from aa_discord_announcements.models import PingTarget, Webhook


@admin.register(PingTarget)
class PingTargetAdmin(admin.ModelAdmin):
    """
    DiscordPingTargetsAdmin
    """

    list_display = (
        "_name",
        "discord_id",
        "_restricted_to_group",
        "notes",
        "is_enabled",
    )

    filter_horizontal = ("restricted_to_group",)
    readonly_fields = ("discord_id",)
    ordering = ("name",)

    @classmethod
    def _name(cls, obj):
        return obj.name

    _name.short_description = "Ping Target"
    _name.admin_order_field = "name"

    @classmethod
    def _restricted_to_group(cls, obj):
        names = [x.name for x in obj.restricted_to_group.all().order_by("name")]

        if names:
            return ", ".join(names)

        return None

    _restricted_to_group.short_description = "Restricted to"
    _restricted_to_group.admin_order_field = "restricted_to_group__name"


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    """
    WebhookAdmin
    """

    list_display = (
        "_name",
        "_url",
        "_restricted_to_group",
        "notes",
        "is_enabled",
    )

    filter_horizontal = ("restricted_to_group",)
    ordering = ("name",)

    @classmethod
    def _name(cls, obj):
        return obj.name

    _name.short_description = "Channel Name"
    _name.admin_order_field = "name"

    @classmethod
    def _url(cls, obj):
        return obj.url

    _url.short_description = "Webhook URL"
    _url.admin_order_field = "url"

    @classmethod
    def _restricted_to_group(cls, obj):
        names = [x.name for x in obj.restricted_to_group.all().order_by("name")]

        if names:
            return ", ".join(names)

        return None

    _restricted_to_group.short_description = "Restricted to"
    _restricted_to_group.admin_order_field = "restricted_to_group__name"

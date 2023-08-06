"""
The models
"""

# Standard Library
import re

# Third Party
from requests.exceptions import HTTPError

# Django
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

# AA Discord Announcements
from aa_discord_announcements.app_settings import discord_service_installed
from aa_discord_announcements.constants import DISCORD_WEBHOOK_REGEX

if discord_service_installed():
    # Alliance Auth
    from allianceauth.services.modules.discord.models import DiscordUser


class General(models.Model):
    """
    Meta model for app permissions
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        General :: Meta
        """

        managed = False
        default_permissions = ()
        permissions = (("basic_access", "Can access this app"),)


class PingTarget(models.Model):
    """
    Discord Ping Targets
    """

    # Discord group to ping
    name = models.OneToOneField(
        Group,
        related_name="discord_announcement_pingtarget",
        on_delete=models.CASCADE,
        unique=True,
        help_text=(
            _(
                "Name of the Discord role to ping. "
                "(Note: This must be an Auth group that is synced to Discord.)"
            )
        ),
    )

    # Discord group id
    discord_id = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        help_text=_("ID of the Discord role to ping"),
    )

    # Restrictions
    restricted_to_group = models.ManyToManyField(
        Group,
        blank=True,
        related_name="discord_announcement_pingtarget_required_groups",
        help_text=_("Restrict ping rights to the following group(s) ..."),
    )

    # Notes
    notes = models.TextField(
        default="",
        blank=True,
        help_text=_("You can add notes about this configuration here if you want"),
    )

    # Is this group active
    is_enabled = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Whether this ping target is enabled or not"),
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """
        DiscordPingTargets :: Meta
        """

        verbose_name = _("Discord Ping Target")
        verbose_name_plural = _("Discord Ping Targets")
        default_permissions = ()

    def __str__(self) -> str:
        return str(self.name)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """
        Add the Discord group ID (if Discord service is active) and save the whole thing
        """

        # Check if the Discord service is active
        if discord_service_installed():
            discord_group_info = DiscordUser.objects.group_to_role(self.name)
            self.discord_id = discord_group_info["id"]

        super().save()  # Call the "real" save() method.

    def clean(self):
        """
        Check if the group has already been synced to Discord,
        if not, raise an error
        """

        # Check if the Discord service is active
        if not discord_service_installed():
            raise ValidationError(
                _("You might want to install the Discord service first ...")
            )

        # Get the group id from Discord
        try:
            discord_group_info = DiscordUser.objects.group_to_role(self.name)
        except HTTPError as http_error:
            raise ValidationError(
                _("Are you sure you have your Discord linked to your Alliance Auth?")
            ) from http_error
        else:
            if not discord_group_info:
                raise ValidationError(
                    _("This group has not been synced to Discord yet.")
                )

        super().clean()


class Webhook(models.Model):
    """
    A Discord webhook
    """

    # Channel name
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text=_("Name of the channel this webhook posts to"),
    )

    # Wehbook url
    url = models.CharField(
        max_length=255,
        unique=True,
        help_text=(
            _(
                "URL of this webhook, e.g. "
                "https://discord.com/api/webhooks/123456/abcdef"
            )
        ),
    )

    # Restrictions
    restricted_to_group = models.ManyToManyField(
        Group,
        blank=True,
        related_name="discord_announcement_webhook_required_groups",
        help_text=_("Restrict ping rights to the following group(s) ..."),
    )

    # Webhook notes
    notes = models.TextField(
        default="",
        blank=True,
        help_text=_("You can add notes about this webhook here if you want"),
    )

    # Is it enabled
    is_enabled = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Whether this webhook is active or not"),
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Webhook :: Meta
        """

        verbose_name = _("Webhook")
        verbose_name_plural = _("Webhooks")
        default_permissions = ()

    def __str__(self) -> str:
        return str(self.name)

    def clean(self):
        """
        Check if the webhook URL is valid
        :return:
        """

        # Check if it's a valid Discord webhook URL
        if not re.match(DISCORD_WEBHOOK_REGEX, self.url):
            raise ValidationError(
                _(
                    "Invalid webhook URL. The webhook URL you entered does not match "
                    "any known format for a Discord webhook. Please check the "
                    "webhook URL."
                )
            )

        super().clean()

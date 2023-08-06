"""
App config
"""

# Django
from django.apps import AppConfig

# AA Discord Announcements
from aa_discord_announcements import __version__


class AaDiscordAnnouncementsConfig(AppConfig):
    """
    Application config
    """

    name = "aa_discord_announcements"
    label = "aa_discord_announcements"
    verbose_name = f"Discord Announcements v{__version__}"

"""
Test checks for installed modules we might use
"""

# Django
from django.test import TestCase, modify_settings

# AA Discord Announcements
from aa_discord_announcements.app_settings import discord_service_installed


class TestModulesInstalled(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up groups and users
        """

        super().setUpClass()

    @modify_settings(INSTALLED_APPS={"remove": "allianceauth.services.modules.discord"})
    def test_for_discord_service_installed_when_not_installed(self):
        """
        Test for discord_service_installed when it is not
        :return:
        """

        self.assertFalse(discord_service_installed())

    @modify_settings(INSTALLED_APPS={"append": "allianceauth.services.modules.discord"})
    def test_for_discord_service_installed_when_installed(self):
        """
        Test for discord_service_installed when it is installed
        :return:
        """

        self.assertTrue(discord_service_installed())

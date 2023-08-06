"""
App Settings
"""

# Django
from django.apps import apps


def discord_service_installed() -> bool:
    """
    Check if the Discord service is installed
    :return: bool
    """

    return apps.is_installed("allianceauth.services.modules.discord")

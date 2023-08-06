"""
Handling Discord webhooks
"""

# Third Party
from dhooks_lite import Webhook

# Django
from django.contrib.auth.models import User
from django.utils import dateformat, timezone

# AA Discord Announcements
from aa_discord_announcements.helper.announcement_context import (
    get_webhook_announcement_context,
)


def send_to_discord_webhook(announcement_context: dict, user: User):
    """
    Send announcement to a Discord webhook
    :param announcement_context:
    :param user:
    :return:
    """

    discord_webhook = Webhook(announcement_context["announcement_channel"]["webhook"])
    webhook_announcement_context = get_webhook_announcement_context(
        announcement_context=announcement_context
    )
    message_body = webhook_announcement_context["content"]
    author_eve_name = user.profile.main_character.character_name

    message_footer = (
        f"_Sent by {author_eve_name} "
        f"@ {dateformat.format(timezone.now(), 'Y-m-d H:i')} (Eve Time)_"
    )
    message_to_send = f"{message_body}\n\n{message_footer}"

    discord_webhook.execute(
        content=message_to_send,
        wait_for_response=True,
    )

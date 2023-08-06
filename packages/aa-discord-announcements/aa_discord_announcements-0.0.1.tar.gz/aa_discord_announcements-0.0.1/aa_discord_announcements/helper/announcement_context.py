"""
Handling announcement context data
"""

# AA Discord Announcements
from aa_discord_announcements.models import PingTarget, Webhook


def get_announcement_context_from_form_data(form_data: dict) -> dict:
    """
    Getting announcement context from form data
    :param form_data:
    :return:
    """

    announcement_target_group_id = None
    announcement_target_group_name = None
    announcement_target_at_mention = None

    if form_data["announcement_target"]:
        if (
            form_data["announcement_target"] == "@here"
            or form_data["announcement_target"] == "@everyone"
        ):
            announcement_target_at_mention = str(form_data["announcement_target"])
        else:
            try:
                # Check if we deal with a custom announcement target
                announcement_target = PingTarget.objects.get(
                    discord_id=form_data["announcement_target"]
                )
            except PingTarget.DoesNotExist:
                pass
            else:
                # We deal with a custom ping target, gather the information we need
                announcement_target_group_id = int(announcement_target.discord_id)
                announcement_target_group_name = str(announcement_target.name)
                announcement_target_at_mention = (
                    str(announcement_target.name)
                    if str(announcement_target.name).startswith("@")
                    else f"@{announcement_target.name}"
                )

    # Check for webhooks
    announcement_channel_webhook = None

    if form_data["announcement_channel"]:
        try:
            announcement_channel = Webhook.objects.get(
                pk=form_data["announcement_channel"]
            )
        except Webhook.DoesNotExist:
            pass
        else:
            announcement_channel_webhook = announcement_channel.url

    announcement_context = {
        "announcement_target": {
            "group_id": int(announcement_target_group_id)
            if announcement_target_group_id
            else None,
            "group_name": str(announcement_target_group_name),
            "at_mention": str(announcement_target_at_mention)
            if announcement_target_at_mention
            else "",
        },
        "announcement_channel": {"webhook": announcement_channel_webhook},
        "announcement_text": str(form_data["announcement_text"]),
    }

    return announcement_context


def get_webhook_announcement_context(announcement_context: dict) -> dict:
    """
    Getting the webhook announcement context
    :param announcement_context:
    :return:
    """

    webhook_announcement_text_content = ""
    webhook_announcement_text_footer = ""
    webhook_announcement_target = ""

    # Ping target
    if announcement_context["announcement_target"]["group_id"]:
        announcement_target_at_mention = (
            f'<@&{announcement_context["announcement_target"]["group_id"]}>'
        )
    else:
        announcement_target_at_mention = (
            f'{announcement_context["announcement_target"]["at_mention"]}'
        )

    if announcement_target_at_mention != "":
        webhook_announcement_text_content += announcement_target_at_mention

    if announcement_context["announcement_text"]:
        webhook_announcement_text_content += (
            f'\n\n{announcement_context["announcement_text"]}'
        )

    return {
        "target": webhook_announcement_target,
        "content": webhook_announcement_text_content,
        "footer": webhook_announcement_text_footer,
    }

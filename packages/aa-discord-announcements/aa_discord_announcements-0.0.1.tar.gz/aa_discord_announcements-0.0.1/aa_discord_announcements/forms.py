"""
The forms
"""

# Django
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


def _get_mandatory_form_label_text(text: str) -> str:
    """
    Label text for mandatory form fields
    :param text:
    :type text:
    :return:
    :rtype:
    """

    required_text = _("This field is mandatory")
    required_marker = (
        f'<span aria-label="{required_text}" class="form-required-marker">*</span>'
    )

    return mark_safe(
        f'<span class="form-field-required">{text} {required_marker}</span>'
    )


class AnnouncementForm(forms.Form):
    """
    Announcement Form
    """

    announcement_target = forms.CharField(
        required=False,
        label=_("Announcement Target"),
        widget=forms.Select(choices={}),
        help_text=_("Who do you want to ping?"),
    )
    announcement_channel = forms.CharField(
        required=False,
        label=_("Announcement Channel"),
        widget=forms.Select(choices={}),
        help_text=_("Select a channel to send the announcement to automatically"),
    )
    announcement_text = forms.CharField(
        required=True,
        label=_get_mandatory_form_label_text(_("Announcement Text")),
        widget=forms.Textarea(
            attrs={
                "rows": 10,
                "cols": 20,
                "input_type": "textarea",
                "placeholder": _("Your announcement ...."),
            }
        ),
    )

"""
Tests for the template tags
"""

# Django
from django.template import Context, Template
from django.test import TestCase

# AA Discord Announcements
from aa_discord_announcements import __version__


class TestVersionedStatic(TestCase):
    """
    Test aa_discord_announcements_versioned_static
    """

    def test_versioned_static(self):
        """
        Test versioned static template tag
        :return:
        """

        context = Context({"version": __version__})
        template_to_render = Template(
            "{% load aa_discord_announcements_versioned_static %}"
            "{% aa_discord_announcements_static 'aa_discord_announcements/css/aa-discord-announcements.min.css' %}"
        )

        rendered_template = template_to_render.render(context)

        self.assertInHTML(
            f'/static/aa_discord_announcements/css/aa-discord-announcements.min.css?v={context["version"]}',
            rendered_template,
        )

"""
Test ajax calls
"""

# Standard Library
from http import HTTPStatus

# Django
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

# AA Discord Announcements
from aa_discord_announcements.tests.utils import create_fake_user


class TestAccess(TestCase):
    """
    Test access to ajax calls
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up groups and users
        """

        super().setUpClass()

        cls.group = Group.objects.create(name="Superhero")

        # User cannot access aa_discord_announcements
        cls.user_1001 = create_fake_user(1001, "Peter Parker")

        # User can access aa_discord_announcements
        cls.user_1002 = create_fake_user(
            1002, "Bruce Wayne", permissions=["aa_discord_announcements.basic_access"]
        )

    def test_ajax_get_announcement_targets_no_access(self):
        """
        Test ajax call to get announcement targets available for
        the current user without access to it
        :return:
        """

        # given
        self.client.force_login(self.user_1001)

        # when
        res = self.client.get(
            reverse("aa_discord_announcements:ajax_get_announcement_targets")
        )

        # then
        self.assertEqual(res.status_code, HTTPStatus.FOUND)

    def test_ajax_get_announcement_targets_general(self):
        """
        Test ajax call to get announcement targets available for the current user
        :return:
        """

        # given
        self.client.force_login(self.user_1002)

        # when
        res = self.client.get(
            reverse("aa_discord_announcements:ajax_get_announcement_targets")
        )

        # then
        self.assertEqual(res.status_code, HTTPStatus.OK)

    def test_ajax_get_webhooks_no_access(self):
        """
        Test ajax call to get webhooks available for
        the current user without access to it
        :return:
        """

        # given
        self.client.force_login(self.user_1001)

        # when
        res = self.client.get(reverse("aa_discord_announcements:ajax_get_webhooks"))

        # then
        self.assertEqual(res.status_code, HTTPStatus.FOUND)

    def test_ajax_get_webhooks_general(self):
        """
        Test ajax call to get webhooks available for the current user
        :return:
        """

        # given
        self.client.force_login(self.user_1002)

        # when
        res = self.client.get(reverse("aa_discord_announcements:ajax_get_webhooks"))

        # then
        self.assertEqual(res.status_code, HTTPStatus.OK)

    def test_ajax_create_announcement_no_access(self):
        """
        Test ajax call to create announcement available for
        a user without access to it
        :return:
        """

        # given
        self.client.force_login(self.user_1001)

        # when
        res = self.client.get(
            reverse("aa_discord_announcements:ajax_create_announcement")
        )

        # then
        self.assertEqual(res.status_code, HTTPStatus.FOUND)

    def test_ajax_create_announcement_general(self):
        """
        Test ajax call to create announcement for the current user
        :return:
        """

        # given
        self.client.force_login(self.user_1002)

        # when
        res = self.client.get(
            reverse("aa_discord_announcements:ajax_create_announcement")
        )

        # then
        self.assertEqual(res.status_code, HTTPStatus.OK)

    def test_ajax_create_announcement_with_form_data(self):
        """
        Test ajax call to create announcement for the current user with form data
        :return:
        """

        # given
        self.client.force_login(self.user_1002)
        form_data = {
            "announcement_target": "@here",
            "announcement_channel": "",
            "announcement_text": "Borg to slaughter!",
        }

        # when
        response = self.client.post(
            reverse("aa_discord_announcements:ajax_create_announcement"), data=form_data
        )

        # then
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(
            response,
            "aa_discord_announcements/partials/announcement/copy-paste-text.html",
        )
        self.assertContains(response, "@here")
        self.assertContains(response, "Borg to slaughter!")

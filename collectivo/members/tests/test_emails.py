"""Tests for using the emails extensions with the members extension."""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from rest_framework.test import APIClient

from collectivo.emails.models import EmailTemplate
from collectivo.emails.tests import CAMPAIGNS_URL, run_mocked_celery_chain
from collectivo.members.models import Member
from collectivo.utils.test import create_testuser

User = get_user_model()


class MembersEmailsTests(TestCase):
    """Tests for using the emails extensions with the members extension."""

    def setUp(self):
        """Prepare test case."""
        super().setUp()
        self.client = APIClient()
        self.user = create_testuser(superuser=True)
        self.client.force_authenticate(self.user)
        self.recipient = User.objects.create_user(
            username=f"recipient@example.com",
            email=f"recipient@example.com",
            first_name=f"recipient",
        )
        self.member = Member.objects.create(user=self.recipient, phone="42")
        self.template = EmailTemplate.objects.create(
            name="Members Email Test Template",
            subject="Test",
            body="{{user.first_name}} has phone number {{user.member.phone}}",
        )

    @patch("collectivo.emails.serializers.chain")
    def test_sending_mails_with_member_data(self, chain):
        """Test that member data can be entered in the email template."""
        payload = {
            "send": True,
            "template": self.template.id,
            "recipients": [self.member.pk],
        }
        res = self.client.post(CAMPAIGNS_URL, payload)
        self.assertEqual(res.status_code, 201)
        run_mocked_celery_chain(chain)
        self.assertEqual(
            mail.outbox[0].alternatives[0][0],
            "recipient has phone number 42",
        )

    # TODO: Unfinished feature for new automation system
    # @patch("collectivo.emails.serializers.chain")
    # def test_new_member_automation(self, chain):
    #     """Test that a new member gets an automatic email."""
    #     # Create automation
    #     template = self.client.post(TEMPLATES_URL, self.template_data)
    #     automation = {
    #         "trigger": "new_member",
    #         "template": template.data["id"],
    #     }
    #     automation_res = self.client.post(AUTO_URL, automation)
    #     self.assertEqual(automation_res.status_code, 201)

    #     # Create a new member
    #     user = User.objects.create_user(
    #         username=f"recipient_0{i}@example.com",
    #         first_name=f"recipient_0{i}",
    #         email=f"recipient_0{i}@example.com",
    #     )
    #     Member
    #     res = self.client.post(MEMBERS_CREATE_URL, member)
    #     self.assertEqual(res.status_code, 201)

    #     # Check that the email was sent automatically
    #     run_mocked_celery_chain(chain)
    #     obj = EmailCampaign.objects.get(template=template.data["id"])
    #     automation = EmailAutomation.objects.get(pk=automation_res.data["id"])
    #     self.assertEqual(obj.automation, automation)
    #     self.assertEqual(obj.status, "success")
    #     self.assertEqual(len(mail.outbox), 1)
    #     self.assertEqual(
    #         mail.outbox[0].recipients()[0], "test_user_not_member@example.com"
    #     )

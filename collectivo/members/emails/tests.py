"""Test the features of the emails API."""
from django.test import TestCase
from django.urls import reverse
from collectivo.auth.clients import CollectivoAPIClient
from collectivo.auth.userinfo import UserInfo
from collectivo.members.models import Member
from django.core import mail
from .models import EmailCampaign, EmailAutomation
from unittest.mock import patch
from collectivo.members.tests.test_members import (
    TEST_MEMBER_POST,
    MEMBERS_CREATE_URL,
)

TEMPLATES_URL = reverse("collectivo:collectivo.members.emails:template-list")
CAMPAIGNS_URL = reverse("collectivo:collectivo.members.emails:campaign-list")
DESIGNS_URL = reverse("collectivo:collectivo.members.emails:design-list")
AUTO_URL = reverse("collectivo:collectivo.members.emails:automation-list")


def run_mocked_celery_chain(mocked_chain):
    """Take a called mocked celery chain and run it locally."""
    if mocked_chain.call_args:
        args = list(mocked_chain.call_args[0])
        task = args.pop(0).apply()
        for arg in args:
            task = arg.apply((task.result,))
        return task.result


class EmailsTests(TestCase):
    """Test the members emails API."""

    def setUp(self):
        """Prepare test case."""
        self.client = CollectivoAPIClient()
        self.client.force_authenticate(
            UserInfo(is_authenticated=True, roles=["members_admin"])
        )
        res = self.client.post(
            DESIGNS_URL, {"name": "Test design 2", "body": "TEST {{content}}"}
        )
        self.template_data = {
            "name": "Test template 2",
            "subject": "Test",
            "design": res.data["id"],
            "body": "First name: {{member.first_name}} <br/> "
            "Person type: {{member.person_type}}",
        }
        self.recipients = [
            Member.objects.get(email="test_member_01@example.com").id,
            Member.objects.get(email="test_member_02@example.com").id,
        ]

    def _batch_assertions(self, res):
        """Assert the results of a batch email request."""
        self.assertEqual(res.status_code, 201)
        obj = EmailCampaign.objects.get(pk=res.data["id"])
        self.assertEqual(obj.status, "success")
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[0].recipients()[0], "test_member_01@example.com"
        )
        self.assertEqual(mail.outbox[0].subject, "Test")
        self.assertEqual(
            mail.outbox[0].alternatives[0][0],
            "TEST First name: Test Member 01 <br/> Person type: natural",
        )
        self.assertEqual(
            mail.outbox[0].body,
            "TEST First name: Test Member 01  \nPerson type: natural\n\n",
        )

    @patch("collectivo.members.emails.serializers.chain")
    def test_email_batch_template(self, chain):
        """Test sending a batch of emails using a template."""
        res = self.client.post(TEMPLATES_URL, self.template_data)
        self.assertEqual(res.status_code, 201)
        payload = {
            "send": True,
            "template": res.data["id"],
            "recipients": self.recipients,
        }
        res = self.client.post(CAMPAIGNS_URL, payload)
        self.assertEqual(res.status_code, 201)
        run_mocked_celery_chain(chain)
        self._batch_assertions(res)

    @patch("collectivo.members.emails.serializers.chain")
    def test_new_member_automation(self, chain):
        """Test that a new member gets an automatic email."""
        # Create automation
        template = self.client.post(TEMPLATES_URL, self.template_data)
        automation = {
            "trigger": "new_member",
            "template": template.data["id"],
        }
        automation_res = self.client.post(AUTO_URL, automation)
        self.assertEqual(automation_res.status_code, 201)

        # Create a new member
        member = {
            **TEST_MEMBER_POST,
            "email": "test_user_not_member@example.com",
        }
        res = self.client.post(MEMBERS_CREATE_URL, member)
        self.assertEqual(res.status_code, 201)

        # Check that the email was sent automatically
        run_mocked_celery_chain(chain)
        obj = EmailCampaign.objects.get(template=template.data["id"])
        automation = EmailAutomation.objects.get(pk=automation_res.data["id"])
        self.assertEqual(obj.automation, automation)
        self.assertEqual(obj.status, "success")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].recipients()[0], "test_user_not_member@example.com"
        )

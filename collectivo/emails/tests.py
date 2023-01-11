"""Test the features of the emails API."""
from django.test import TestCase
from django.urls import reverse
from collectivo.auth.clients import CollectivoAPIClient
from collectivo.auth.userinfo import UserInfo
from collectivo.members.models import Member
from django.core import mail
from .models import EmailCampaign
from unittest.mock import patch

TEMPLATES_URL = reverse('collectivo:collectivo.emails:template-list')
BATCHES_URL = reverse('collectivo:collectivo.emails:batch-list')
DESIGNS_URL = reverse('collectivo:collectivo.emails:design-list')


def run_mocked_celery_chain(mocked_chain):
    """Take a called mocked celery chain and run it locally."""
    args = list(mocked_chain.call_args[0])
    task = args.pop(0).apply()
    for arg in args:
        task = arg.apply((task.result,))
    return task.result


class MembersEmailAPITests(TestCase):
    """Test the members emails API."""

    def setUp(self):
        """Prepare test case."""
        self.client = CollectivoAPIClient()
        self.client.force_authenticate(
            UserInfo(is_authenticated=True, roles=['superuser'])
        )
        res = self.client.post(DESIGNS_URL, {'body': 'TEST {{content}}'})
        self.template_data = {
            'subject': 'Test',
            'design': res.data['id'],
            'message': 'First name: {{member.first_name}} <br/> '
                       'Person type: {{member.person_type}}'
        }
        self.recipients = [
            Member.objects.get(email='test_member_01@example.com').id,
            Member.objects.get(email='test_member_02@example.com').id
        ]

    def _batch_assertions(self, res):
        """Assert the results of a batch email request."""
        self.assertEqual(res.status_code, 201)
        obj = EmailCampaign.objects.get(pk=res.data['id'])
        self.assertEqual(obj.status, 'success')
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[0].recipients()[0], 'test_member_01@example.com')
        self.assertEqual(mail.outbox[0].subject, 'Test')
        self.assertEqual(
            mail.outbox[0].alternatives[0][0],
            "TEST First name: Test Member 01 <br/> Person type: natural")
        self.assertEqual(
            mail.outbox[0].body,
            "TEST First name: Test Member 01  \nPerson type: natural\n\n")

    @patch('collectivo.emails.views.chain')
    def test_email_batch_direct(self, chain):
        """Test sending a batch of emails with direct inputs."""
        payload = {
            **self.template_data,
            'recipients': self.recipients
        }
        res = self.client.post(BATCHES_URL, payload)
        run_mocked_celery_chain(chain)
        self._batch_assertions(res)

    @patch('collectivo.emails.views.chain')
    def test_email_batch_template(self, chain):
        """Test sending a batch of emails using a template."""
        res = self.client.post(TEMPLATES_URL, self.template_data)
        self.assertEqual(res.status_code, 201)
        payload = {
            'template': res.data['id'],
            'recipients': self.recipients
        }
        res = self.client.post(BATCHES_URL, payload)
        run_mocked_celery_chain(chain)
        self._batch_assertions(res)

"""Test the features of the emails API."""
from django.test import TestCase
from django.urls import reverse
from collectivo.auth.clients import CollectivoAPIClient
from collectivo.auth.userinfo import UserInfo
from collectivo.members.models import Member
from django.core import mail
from .models import EmailBatch


TEMPLATES_URL = reverse('collectivo:collectivo.emails:template-list')
BATCHES_URL = reverse('collectivo:collectivo.emails:batch-list')
DESIGNS_URL = reverse('collectivo:collectivo.emails:design-list')


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
        obj = EmailBatch.objects.get(pk=res.data['id'])
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

    def test_email_batch_direct(self):
        """Test that a superuser can send a batch of emails."""
        payload = {
            **self.template_data,
            'recipients': self.recipients
        }
        res = self.client.post(BATCHES_URL, payload)
        self._batch_assertions(res)

    def test_email_batch_template(self):
        """Test that a superuser can send a batch of emails with template."""
        res = self.client.post(TEMPLATES_URL, self.template_data)
        self.assertEqual(res.status_code, 201)
        payload = {
            'template': res.data['id'],
            'recipients': self.recipients
        }
        res = self.client.post(BATCHES_URL, payload)
        self._batch_assertions(res)

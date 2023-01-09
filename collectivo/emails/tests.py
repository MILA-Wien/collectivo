"""Test the features of the emails API."""
from django.test import TestCase
from django.urls import reverse
from django.core.mail import send_mail
from collectivo.auth.clients import CollectivoAPIClient
from collectivo.auth.userinfo import UserInfo
from django.core import mail
from .models import EmailTemplate, EmailBatch


TEMPLATES_URL = reverse('collectivo:collectivo.emails:template-list')
BATCHES_URL = reverse('collectivo:collectivo.emails:batch-list')


class PrivateMenusApiTests(TestCase):
    """Test the privatly available menus API."""

    def setUp(self):
        """Prepare test case."""
        self.client = CollectivoAPIClient()
        self.client.force_authenticate(
            UserInfo(is_authenticated=True, roles=['superuser'])
        )

    def _create_email_template(self):
        payload = {
            'subject': 'Test',
            'message': 'Test {{first_name}} <b/> Test'
        }
        return self.client.post(TEMPLATES_URL, payload)

    def test_create_email_template(self):
        """Test that a superuser can create an email template."""
        res = self._create_email_template()
        self.assertEqual(res.status_code, 201)

    def test_send_email_batch(self):
        """Test that a superuser can send a batch of emails."""
        res = self._create_email_template()
        payload = {
            'template': res.data['id'],
            'recipients': [1, 2],
        }
        print('before')
        res = self.client.post(BATCHES_URL, payload)
        print('after')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(len(mail.outbox), 2)
        obj = EmailBatch.objects.get(pk=res.data['id'])
        self.assertEqual(obj.status, 'success')

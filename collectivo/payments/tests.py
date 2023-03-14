"""Test the features of the emails API."""
from django.test import TestCase
from django.urls import reverse
from collectivo.auth.clients import CollectivoAPIClient
from collectivo.auth.userinfo import UserInfo
from collectivo.members.models import Member
from django.core import mail
from .models import EmailCampaign
from unittest.mock import patch

PAYMENTS_URL = reverse("collectivo:collectivo.payments:payment-list")
SUBSCRIPTIONS_URL = reverse("collectivo:collectivo.payments:subscription-list")


class PaymentsTests(TestCase):
    """Test the members emails API."""

    def setUp(self):
        """Prepare test case."""
        self.client = CollectivoAPIClient()
        self.client.force_authenticate(
            UserInfo(is_authenticated=True, roles=["payments_admin"])
        )

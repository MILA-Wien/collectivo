"""Tests of the lotzapp extension."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from mila.lotzapp.models import LotzappSettings
from rest_framework.test import APIClient

from collectivo.payments.models import Invoice, ItemEntry, ItemType
from collectivo.utils.test import create_testadmin, create_testuser

User = get_user_model()

CREATE_INVOICES_URL = reverse("mila.lotzapp:invoice-sync")


class LotzappInvoicesTests(TestCase):
    """Test the connection between lotzapp and the payments extension."""

    def setUp(self):
        """Prepare client and create test user."""
        self.user = create_testuser()
        self.admin = create_testadmin()
        self.client = APIClient()
        self.client.force_authenticate(self.admin)
        self.invoice = Invoice.objects.create(
            payment_from=self.user, status="open"
        )
        ItemEntry.objects.create(
            invoice=self.invoice,
            price=17.5,
            type=ItemType.objects.create(name="Test"),
        )
        self.settings = LotzappSettings.object()

    def test_sync_invoices(self):
        """Test that invoices are synced correctly."""

        res = self.client.post(CREATE_INVOICES_URL)
        self.assertEqual(res.status_code, 400)  # Lotzapp settings empty

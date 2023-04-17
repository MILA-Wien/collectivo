"""Tests of the memberships extension."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.payments.models import Invoice, ItemEntry
from collectivo.utils.test import create_testadmin, create_testuser

from .models import Membership, MembershipType

User = get_user_model()

CREATE_INVOICES_URL = reverse(
    "collectivo:collectivo.memberships:membership-create_invoices"
)


class MembershipsSetupTests(TestCase):
    """Test that the extension is installed correctly."""

    def setUp(self):
        """Initialize testing instance."""
        self.extension = Extension.objects.get(name="memberships")

    def test_menu_items_exist(self):
        """Test that the menu items are registered."""
        res = MenuItem.objects.filter(extension=self.extension)
        self.assertEqual(len(res), 2)


class MembershipsPaymentsTests(TestCase):
    """Test the connection between the memberships and payments extension."""

    def setUp(self):
        """Prepare client and create test user."""
        self.user = create_testuser()
        self.admin = create_testadmin()
        self.client = APIClient()
        self.client.force_authenticate(self.admin)
        self.membership_type = MembershipType.objects.create(
            name="Test Type",
            has_shares=True,
            shares_amount_per_share=15,
        )
        self.membership = Membership.objects.create(
            user=self.user, type=self.membership_type, shares_signed=10
        )

    def test_create_invoices(self):
        """Test that invoices are created correctly."""

        # First invoice
        res = self.client.post(CREATE_INVOICES_URL)
        self.assertEqual(res.status_code, 200)
        entry = ItemEntry.objects.get(
            type__name=self.membership_type.name,
        )
        self.assertEqual(entry.amount, 10)
        self.assertEqual(entry.price, 15)
        self.assertEqual(entry.invoice.payment_from, self.user)
        self.assertEqual(entry.invoice.status, "open")

        # No second invoice if nothing changes
        res = self.client.post(CREATE_INVOICES_URL)
        entries = ItemEntry.objects.filter(
            type__name=self.membership_type.name,
        )
        self.assertEqual(len(entries), 1)

        # Second invoice if shares change
        self.membership.shares_signed = 10 + 3
        self.membership.save()
        res = self.client.post(CREATE_INVOICES_URL)
        entries = ItemEntry.objects.filter(
            type__name=self.membership_type.name,
        )
        self.assertEqual(len(entries), 2)
        entry = entries.last()
        self.assertEqual(entry.amount, 3)

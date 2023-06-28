"""Tests of the memberships extension."""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.emails.models import EmailAutomation
from collectivo.emails.tests import run_mocked_celery_chain
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.payments.models import Invoice, ItemEntry, Subscription
from collectivo.utils.test import create_testadmin, create_testuser

from .models import Membership, MembershipType

User = get_user_model()

MEMBERSHIP_URL_NAME = "collectivo.memberships:membership-detail"


class MembershipsSetupTests(TestCase):
    """Test that the extension is installed correctly."""

    def setUp(self):
        """Initialize testing instance."""
        self.extension = Extension.objects.get(name="memberships")

    def test_menu_items_exist(self):
        """Test that the menu items are registered."""
        res = MenuItem.objects.filter(extension=self.extension)
        self.assertEqual(len(res), 2)


class MembershipsEmailsTests(TestCase):
    """Test the connection between the memberships and emails extension."""

    def setUp(self):
        """Prepare client and create test user."""
        self.user = create_testuser()
        self.user.email = "recipient@example.com"
        self.user.save()
        self.admin = create_testadmin()
        self.client = APIClient()
        self.client.force_authenticate(self.admin)
        self.membership_type = MembershipType.objects.create(
            name="Test Type",
            has_shares=True,
            shares_amount_per_share=15,
        )

        for stage in ["applied", "accepted", "ended"]:
            auto_appl = EmailAutomation.objects.get(name=f"Membership {stage}")
            auto_appl.subject = f"Test Subject {stage}"
            auto_appl.body = (
                f"Test Body {stage}" + " {{ membership.type.name }}"
            )
            auto_appl.is_active = True
            auto_appl.save()

    @patch("collectivo.emails.models.chain")
    def test_automatic_emails(self, chain):
        """Test that automatic emails are sent."""

        self.membership = Membership.objects.create(
            user=self.user, type=self.membership_type, shares_signed=10
        )

        run_mocked_celery_chain(chain)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Test Subject applied")
        self.assertEqual(
            mail.outbox[0].body, "Test Body applied Test Type\n\n"
        )

        self.membership.stage = "accepted"
        self.membership.save()

        run_mocked_celery_chain(chain)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, "Test Subject accepted")


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
        self.subscription_type = MembershipType.objects.create(
            name="Test Type Sub", has_fees=True
        )
        self.membership = Membership.objects.create(
            user=self.user, type=self.membership_type, shares_signed=10
        )
        self.sub_membership = Membership.objects.create(
            user=self.user, type=self.subscription_type, fees_amount=11
        )

    def test_subscription(self):
        """Test that subscriptions are created correctly."""

        sub = Subscription.objects.get(payment_from=self.user.account)
        self.assertEqual(sub.items.first().price, 11)
        self.assertEqual(sub.items.first().amount, 1)
        self.sub_membership.fees_amount = 12
        self.sub_membership.save()
        sub = Subscription.objects.get(payment_from=self.user.account)
        self.assertEqual(sub.items.first().price, 12)
        self.assertEqual(sub.items.first().amount, 1)

    def test_create_invoices(self):
        """Test that invoices are created correctly."""

        # First invoice
        entry = ItemEntry.objects.get(
            type__name=self.membership_type.name,
        )
        self.assertEqual(entry.amount, 10)
        self.assertEqual(entry.price, 15)
        self.assertEqual(entry.invoice.payment_from, self.user.account)
        self.assertEqual(entry.invoice.status, "open")

        # No second invoice if nothing changes
        entries = ItemEntry.objects.filter(
            type__name=self.membership_type.name,
        )
        self.assertEqual(len(entries), 1)

        # Second invoice if shares change
        self.membership.shares_signed = 10 + 3
        self.membership.save()

        entries = ItemEntry.objects.filter(
            type__name=self.membership_type.name,
        )
        self.assertEqual(len(entries), 2)
        entry = entries.last()
        self.assertEqual(entry.amount, 3)

        # Shares paid is shown correctly in membership serializer
        url = reverse(
            MEMBERSHIP_URL_NAME,
            kwargs={"pk": self.membership.pk},
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["shares_paid"], 0)
        entry.invoice.status = "paid"
        entry.invoice.save()
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["shares_paid"], 3)

    def test_update_shares_paid(self):
        """Test that invoices are synced with the payments extension."""

        self.assertEqual(self.membership.shares_paid, 0)
        inv = Invoice.objects.get(payment_from__user=self.user)
        inv.status = "paid"
        inv.save()
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.shares_paid, 10)
        self.membership.shares_signed = 15
        self.membership.save()
        self.assertEqual(self.membership.shares_paid, 10)
        invs = Invoice.objects.filter(payment_from__user=self.user)
        for inv in invs:
            inv.status = "paid"
            inv.save()
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.shares_paid, 15)


class MembershipsTests(TestCase):
    """Test the memberships extension."""

    def setUp(self):
        """Prepare client and create test user."""
        self.user = create_testuser()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.membership_type = MembershipType.objects.create(
            name="Test Type",
            has_shares=True,
            shares_amount_per_share=15,
            shares_number_custom_min=20,
            shares_number_social=10,
        )
        self.membership = Membership.objects.create(
            user=self.user, type=self.membership_type, shares_signed=10
        )

    def test_update_shares(self):
        """Test that the shares can be updated."""
        url = reverse(
            "collectivo.memberships:membership-self-detail",
            args=[self.membership.id],
        )
        payload = {"shares_signed": 20}
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, 200)
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.shares_signed, 20)

    def test_update_shares_lower_fails(self):
        """Test that the shares cannot be updated to a lower number."""
        url = reverse(
            "collectivo.memberships:membership-self-detail",
            args=[self.membership.id],
        )
        payload = {"shares_signed": 1}
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, 400)

    def test_update_shares_below_min_fails(self):
        """Test that the shares cannot be updated to a lower number."""
        url = reverse(
            "collectivo.memberships:membership-self-detail",
            args=[self.membership.id],
        )
        payload = {"shares_signed": 15}
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, 400)

    def test_update_fails(self):
        """Test that other fields than shares cannot be updated."""
        url = reverse(
            "collectivo.memberships:membership-self-detail",
            args=[self.membership.id],
        )
        payload = {"number": 20}
        self.client.patch(url, payload)
        self.assertNotEqual(self.membership.number, 20)

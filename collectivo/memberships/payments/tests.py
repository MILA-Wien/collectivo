"""Tests of the memberships extension."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from collectivo.payments.models import Payment, Subscription
from collectivo.utils.test import create_testuser

from ..models import Membership, MembershipType

User = get_user_model()


class MembershipSharesTests(TestCase):
    """Tests of the membership shares connection."""

    def setUp(self):
        """Prepare client, extension, & micro-frontend."""
        self.client = APIClient()
        self.client_user = create_testuser(superuser=True)
        self.client.force_authenticate(self.client_user)

        self.user = User.objects.create_user(username="user_with_shares")
        self.membership_type = MembershipType.objects.create(
            name="Tests",
            has_shares=True,
            shares_amount_per_share=100,
            shares_number_custom=True,
        )
        self.membership = Membership.objects.create(
            user=self.user,
            type=self.membership_type,
            shares_signed=5,
        )

    def test_shares_payment(self):
        """Test automatic shares payment is created."""
        payment = Payment.objects.filter(payer=self.user.id).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.amount, 500)
        self.assertEqual(
            payment.membership_shares.first().membership, self.membership
        )

    def test_shares_payment_update(self):
        """Test that another payment is created if shares are increased."""
        self.membership.shares_signed = 11
        self.membership.save()

        payments = Payment.objects.filter(payer=self.user.id)
        self.assertEqual(len(payments), 2)
        payment = payments.last()
        self.assertEqual(payment.amount, 600)
        self.assertEqual(
            payment.membership_shares.first().membership, self.membership
        )

    def test_pay_shares(self):
        """Test that shares are paid when payment is successful."""
        payment = Payment.objects.filter(payer=self.user.id).first()
        payment.status = "success"
        payment.save()

        self.membership.refresh_from_db()
        self.assertEqual(self.membership.shares_paid, 5)

    def test_pay_shares_update(self):
        """Test that shares are paid when a second payment is successful."""
        self.membership.shares_signed = 11
        self.membership.save()

        for payment in self.membership.payments.shares_payments.all():
            payment.status = "success"
            payment.save()

        self.membership.refresh_from_db()
        self.assertEqual(self.membership.shares_paid, 11)


class MembershipFeesTests(TestCase):
    """Tests of the membership fees connection."""

    def setUp(self):
        """Prepare client, extension, & micro-frontend."""
        self.client = APIClient()
        self.client_user = create_testuser(superuser=True)
        self.client.force_authenticate(self.client_user)

        self.user = User.objects.create_user(username="user_with_fees")
        self.membership_type = MembershipType.objects.create(
            name="Tests",
            has_fees=True,
            fees_amount_standard=100,
        )
        self.membership = Membership.objects.create(
            user=self.user,
            type=self.membership_type,
            shares_signed=5,
        )

    def test_fees_subscription(self):
        """Test automatic shares payment is created."""
        sub = Subscription.objects.filter(payer=self.user.id).first()
        self.assertEqual(sub.amount, 100)
        self.assertEqual(
            sub.membership_fees.first().membership, self.membership
        )

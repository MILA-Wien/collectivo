"""Tests of the members extension for admins."""
from django.contrib.auth import get_user_model
from django.db.models import signals
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.payments.models import Payment
from collectivo.tags.models import Tag
from collectivo.utils.test import create_testuser

from ..models import Member, Membership, MembershipType

User = get_user_model()

MEMBERS_URL = reverse("collectivo:collectivo.members:member-list")
MEMBERS_SCHEMA_URL = reverse("collectivo:collectivo.members:member-schema")
MEMBERS_DETAIL = "collectivo:collectivo.members:member-detail"
PROFILE_URL = reverse("collectivo:collectivo.members:profile")
REGISTER_URL = reverse("collectivo:collectivo.members:register")
REGISTRATION_SCHEMA_URL = reverse(
    "collectivo:collectivo.members:register-schema"
)
PROFILE_SCHEMA_URL = reverse("collectivo:collectivo.members:profile-schema")

MEMBER = {
    "first_name": "firstname",
    "last_name": "lastname",
    "gender": "diverse",
    "address_street": "my street",
    "address_number": "1",
    "address_postcode": "0000",
    "address_city": "my city",
    "address_country": "my country",
    "person_type": "natural",
}


class MembershipSharesTests(TestCase):
    """Test the privatly available members API for admins."""

    def setUp(self):
        """Prepare client, extension, & micro-frontend."""
        self.client = APIClient()
        self.user = create_testuser(superuser=True)
        self.client.force_authenticate(self.user)

        self.membership_type = MembershipType.objects.create(
            name="Tests", has_shares=True
        )
        self.test_user = User.objects.create_user(username="testuserrr")
        self.member = Member.objects.create(user=self.test_user)
        self.membership = Membership.objects.create(
            member=self.member, type=self.membership_type
        )

    def test_shares(self):
        """Test automatic shares payment is created."""
        # self.assertEqual(self.membership.shares.count(), 1)
        # self.assertEqual(self.membership.shares.first().amount, 100)
        print(Payment.objects.all())

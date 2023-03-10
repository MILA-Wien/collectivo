"""Tests of the members extension for admins."""
# TODO: Reintroduce filtering tests from filter branch
from django.contrib.auth import get_user_model
from django.db.models import signals
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.utils.tests import create_testuser

from ..models import Member

User = get_user_model()

MEMBERS_URL = reverse("collectivo:collectivo.members:member-list")
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


class MembersAdminTests(TestCase):
    """Test the privatly available members API for admins."""

    def setUp(self):
        """Prepare client, extension, & micro-frontend."""
        self.client = APIClient()
        self.user = create_testuser(superuser=True)
        self.client.force_authenticate(self.user)
        Member.objects.all().delete()

    def create_members(self):
        """Create an unordered set of members for testing."""
        signals.post_save.disconnect(
            sender=User, dispatch_uid="update_keycloak_user"
        )
        ids = []
        for i in [0, 2, 1]:
            user = User.objects.create_user(
                username=str(i),
                email=str(i) + "@example.com",
                first_name=str(i),
            )
            payload = {**MEMBER, "user": user.id}
            self.client.post(MEMBERS_URL, payload)
            ids.append(user.id)
        return ids

    def test_create_members(self):
        """Test that admins can create members."""
        self.create_members()
        self.assertEqual(len(Member.objects.all()), 3)

    def test_get_members(self):
        """Get members."""
        id = self.create_members()[0]
        res = self.client.get(MEMBERS_URL)
        self.assertEqual(res.status_code, 200)
        data = res.data[0]
        self.assertEqual(data["user"], id)
        self.assertEqual(data["user__first_name"], "0")

    def test_update_member(self):
        """Test that admins can write to admin fields."""
        user_id = self.create_members()[0]
        res = self.client.patch(
            reverse(MEMBERS_DETAIL, args=[user_id]),
            data={"notes": "my note"},
        )
        self.assertEqual(res.status_code, 200)
        member = Member.objects.get(user=user_id)
        self.assertEqual(getattr(member, "notes"), "my note")

    def test_sorting(self):
        """Test that all member fields can be sorted."""
        self.create_members()

        res = self.client.get(MEMBERS_URL + "?ordering=user__first_name")
        self.assertEqual(
            [entry["user__first_name"] for entry in res.data], ["0", "1", "2"]
        )

        res = self.client.get(MEMBERS_URL + "?ordering=-user__first_name")
        self.assertEqual(
            [entry["user__first_name"] for entry in res.data], ["2", "1", "0"]
        )

    def test_pagination(self):
        """Test that pagination works for members."""
        self.create_members()

        limit = 1
        offset = 1
        res = self.client.get(MEMBERS_URL + f"?limit={limit}&offset={offset}")
        self.assertEqual(
            [entry["user__first_name"] for entry in res.data["results"]],
            ["2"],
        )

    def test_new_users_are_added_to_members_user_group(self):
        """Test that new users are added to the members group."""
        user = User.objects.create(username="another_user")
        self.assertTrue(
            user.groups.filter(name="collectivo.members.user").exists()
        )

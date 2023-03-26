"""Tests of the members extension for admins."""
from django.contrib.auth import get_user_model
from django.db.models import signals
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.tags.models import Tag
from collectivo.utils.test import create_testuser

from ..profiles.models import MemberProfile, Membership, MembershipType

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


class MembersAdminTests(TestCase):
    """Test the privatly available members API for admins."""

    def setUp(self):
        """Prepare client, extension, & micro-frontend."""
        self.client = APIClient()
        self.user = create_testuser(superuser=True)
        self.client.force_authenticate(self.user)
        self.membership_type = MembershipType.objects.create(name="Testss")
        MemberProfile.objects.all().delete()

    def create_members(self):
        """Create an unordered set of members for testing."""
        signals.post_save.disconnect(
            sender=User, dispatch_uid="update_keycloak_user"
        )
        ids = []
        tag_ids = []
        other_tag = Tag.objects.get_or_create(name="Other tag")[0]
        for i in [0, 2, 1]:
            # Create a user
            user = User.objects.create_user(
                username=str(i),
                email=str(i) + "@example.com",
                first_name=str(i),
            )
            ids.append(user.id)

            # Add tags to this user
            tag = Tag.objects.get_or_create(name=f"Tag {i}")[0]
            tag.users.add(user)
            other_tag.users.add(user)
            other_tag.save()
            tag.save()
            tag_ids.append(tag.id)

            # Create a member for this user
            payload = {**MEMBER, "user": user.id}
            self.client.post(MEMBERS_URL, payload)
            profile = MemberProfile.objects.get(user=user)

            # Create a membership for this member
            Membership.objects.create(
                profile=profile, type=self.membership_type
            )

        tag_ids.append(other_tag.id)
        return ids, tag_ids

    def test_create_members(self):
        """Test that admins can create members."""
        self.create_members()
        self.assertEqual(len(MemberProfile.objects.all()), 3)

    def test_get_members(self):
        """Get members."""
        user_ids, tag_ids = self.create_members()
        res = self.client.get(MEMBERS_URL)
        self.assertEqual(res.status_code, 200)
        for i, j in enumerate([0, 2, 1]):
            data = res.data[i]
            self.assertEqual(data["user"], user_ids[i])
            self.assertEqual(data["user__first_name"], str(j))
            for tag_id in [tag_ids[i], tag_ids[-1]]:
                self.assertIn(tag_id, data["user__tags"])

    def test_update_member(self):
        """Test that admins can write to admin fields."""
        user_id = self.create_members()[0][0]
        res = self.client.patch(
            reverse(MEMBERS_DETAIL, args=[user_id]),
            data={"notes": "my note"},
        )
        self.assertEqual(res.status_code, 200)
        member = MemberProfile.objects.get(user=user_id)
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

    def test_filtering(self):
        """Test that member names can be filtered with 'contains'."""
        ids, tag_ids = self.create_members()
        res = self.client.get(MEMBERS_URL + "?user__first_name__contains=1")
        self.assertEqual(
            [entry["user__first_name"] for entry in res.data], ["1"]
        )
        id_strings = ",".join([str(i) for i in ids])
        res = self.client.get(MEMBERS_URL + "?id__in=" + id_strings)
        self.assertEqual(
            [entry["user__first_name"] for entry in res.data], ["0", "2", "1"]
        )
        res = self.client.get(MEMBERS_URL + "?person_type=legal")
        self.assertEqual(res.data, [])
        res = self.client.get(MEMBERS_URL + "?person_type__isnull=True")
        self.assertEqual(res.data, [])
        res = self.client.get(MEMBERS_URL + "?person_type__isnull=False")
        self.assertEqual(
            [entry["user__first_name"] for entry in res.data], ["0", "2", "1"]
        )

    def test_filtering_tags(self):
        """Test that member tags can be filtered."""
        _, tag_ids = self.create_members()
        for i, j in enumerate([0, 2, 1]):
            res = self.client.get(MEMBERS_URL + f"?user__tags={tag_ids[i]}")
            self.assertEqual(
                [entry["user__first_name"] for entry in res.data], [str(j)]
            )
            res = self.client.get(
                MEMBERS_URL
                + f"?user__tags={tag_ids[i]}&user__tags={tag_ids[-1]}"
            )
            self.assertEqual(
                [entry["user__first_name"] for entry in res.data], [str(j)]
            )
        res = self.client.get(MEMBERS_URL + f"?user__tags={tag_ids[-1]}")
        self.assertEqual(
            [entry["user__first_name"] for entry in res.data], ["0", "2", "1"]
        )

    def test_schema_choices_url(self):
        """Test that the choices url can be retrieved through the schema."""
        self.create_members()
        res = self.client.get(MEMBERS_SCHEMA_URL)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.data["user__tags"]["choices_url"], "/api/tags/tags/"
        )

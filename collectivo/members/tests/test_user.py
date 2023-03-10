"""Tests of the members extension for users."""
from django.contrib.auth import get_user_model
from django.db.models import signals
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import localdate
from rest_framework.test import APIClient

from collectivo.tags.models import Tag
from collectivo.utils.tests import create_testuser

from .. import models
from ..models import Member

User = get_user_model()

MEMBERS_URL = reverse("collectivo:collectivo.members:member-list")
MEMBER_URL_LABEL = "collectivo:collectivo.members:member-detail"
PROFILE_URL = reverse("collectivo:collectivo.members:profile")
REGISTER_URL = reverse("collectivo:collectivo.members:register")
REGISTER_SCHEMA_URL = reverse("collectivo:collectivo.members:register-schema")
REGISTRATION_SCHEMA_URL = reverse(
    "collectivo:collectivo.members:register-schema"
)
PROFILE_SCHEMA_URL = reverse("collectivo:collectivo.members:profile-schema")

TEST_MEMBER = {
    "gender": "diverse",
    "address_street": "my street",
    "address_number": "1",
    "address_postcode": "0000",
    "address_city": "my city",
    "address_country": "my country",
}

TEST_MEMBER_POST = {
    **TEST_MEMBER,
    "person_type": "natural",
    "membership_type": "active",
    "survey_contact": "-",
    "survey_motivation": "-",
    "shares_payment_type": "sepa",
    "statutes_approved": True,
    "shares_tarif": "normal",
}

TEST_MEMBER_GET = {
    **TEST_MEMBER,
    # "membership_start": localdate(),
    # "email": "some_member@example.com",
}

TEST_USER = {
    "email": "some_member@example.com",
    "username": "some_member@example.com",
    "firstName": "firstname",
    "lastName": "lastname",
}


class MembersPublicApiTests(TestCase):
    """Test the public members API."""

    def setUp(self):
        """Prepare client."""
        self.client = APIClient()

    def test_auth_required_for_members(self):
        """Test that authentication is required for /members."""
        res = self.client.get(MEMBERS_URL)
        self.assertEqual(res.status_code, 401)

    def test_auth_required_for_profile(self):
        """Test that authentication is required for /profile."""
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, 401)


class MembersRegistrationTests(TestCase):
    """Test the private members API for users that are not members."""

    def setUp(self):
        """Prepare client and create test user."""
        self.client = APIClient()
        self.user = create_testuser(TEST_USER)
        self.client.force_authenticate(self.user)
        self.status = models.MembershipStatus.objects.filter(
            type__label="Genossenschaft MILA"
        )[0]

    def test_cannot_access_profile(self):
        """Test that a user cannot access profile if they are not a member."""
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(
            res.data["detail"], "User is not registered as a member."
        )

    def create_member(self, payload=TEST_MEMBER_POST):
        """Create a sample member."""
        res = self.client.post(
            REGISTER_URL, {**payload, "membership_status": self.status.id}
        )
        member = Member.objects.get(user=res.data["user"])
        return member

    def test_create_member(self):
        """Test that an authenticated user can create itself as a member."""
        member = self.create_member()
        for key, value in TEST_MEMBER_GET.items():
            self.assertEqual(value, getattr(member, key))

        memberships = member.membership_set.all()
        self.assertEqual(len(memberships), 1)
        membership = memberships[0]
        self.assertEqual(membership.status, self.status)
        self.assertEqual(membership.shares, 9)

    def test_tags_assigned(self):
        """Test that tags are assigned to the user when a member is created."""
        member = self.create_member()
        tag = Tag.objects.get_or_create(label="Statuten angenommen")[0]
        self.assertIn(tag, member.user.tag_set.all())
        tag = Tag.objects.get_or_create(label="Öffentlichkeitsarbeit")[0]
        self.assertNotIn(tag, member.user.tag_set.all())

    def test_statutes_not_approved_raises_error(self):
        """Test that statutes must be approved."""
        res = self.client.post(
            REGISTER_URL,
            {
                **TEST_MEMBER_POST,
                "membership_status": self.status.id,
                "statutes_approved": False,
            },
        )
        self.assertEqual(res.status_code, 400)

    # Test invalid payloads

    # def test_get_schema(self):
    #     """Test that an authenticated user can create itself as a member."""
    #     res = self.client.get(REGISTER_SCHEMA_URL)
    #     print(res.data)


#     def test_create_legal_member(self):
#         """Test that a legal member automatically becomes type investing."""
#         payload = {**TEST_MEMBER_POST, "person_type": "legal"}
#         member = self.create_member(payload)
#         self.assertEqual(member.membership_type, "investing")

#     def test_create_member_tags_missing(self):
#         """Test that unchecked tag fields do not become tags."""
#         member = self.create_member()
#         self.assertFalse(
#             member.tags.filter(label="Public use approved").exists()
#         )

#     def test_create_member_tags(self):
#         """Test that checked tag fields become tags."""
#         payload = {**TEST_MEMBER_POST, "public_use_approved": True}
#         member = self.create_member(payload)
#         self.assertTrue(
#             member.tags.filter(label="Public use approved").exists()
#         )

#     def test_multiple_choice_str(self):
#         """Test that multiple choices can be selected with strings."""
#         payload = {**TEST_MEMBER_POST, "groups_interested": ["1", "2", "3"]}
#         member = self.create_member(payload)
#         group_ids = [group.id for group in member.groups_interested.all()]
#         self.assertEqual(group_ids, [1, 2, 3])

#     def test_multiple_choice_with_int(self):
#         """Test that multiple choices can be selected with numbers."""
#         payload = {**TEST_MEMBER_POST, "groups_interested": [1, 2, 3]}
#         member = self.create_member(payload)
#         group_ids = [group.id for group in member.groups_interested.all()]
#         self.assertEqual(group_ids, [1, 2, 3])


# class PrivateMemberApiTestsForMembers(MembersTestCase):
#     """Test the private members API for users that are members."""

#     def setUp(self):
#         """Register authorized user as member."""
#         super().setUp()
#         res = self.client.post(REGISTER_URL, TEST_MEMBER_POST)
#         if res.status_code != 201:
#             raise Exception("Could not register member:", res.content)
#         self.members_id = res.data["id"]

#     def test_member_cannot_access_admin_area(self):
#         """Test that a normal member cannot access admin API."""
#         res = self.client.get(MEMBERS_URL)
#         self.assertEqual(res.status_code, 403)

#     def test_cannot_create_same_member_twice(self):
#         """Test that a member cannot create itself as a member again."""
#         res2 = self.client.post(REGISTER_URL, TEST_MEMBER_POST)
#         self.assertEqual(res2.status_code, 403)

#     def test_get_profile(self):
#         """Test that a member can view it's own data."""
#         res = self.client.get(PROFILE_URL)
#         self.assertEqual(res.status_code, 200)
#         for key, value in TEST_MEMBER_GET.items():
#             self.assertEqual(str(value), str(res.data[key]))

#     def test_update_member(self):
#         """Test that a member can edit non-admin fields of it's own data."""
#         self.client.patch(PROFILE_URL, {"address_street": "my_street"})
#         res = self.client.get(PROFILE_URL)
#         self.assertEqual(res.data["address_street"], "my_street")

#     def test_update_member_admin_fields_fails(self):
#         """Test that a member cannot edit admin fields of it's own data."""
#         self.client.patch(PROFILE_URL, {"admin_notes": "my note"})
#         member = Member.objects.get(id=self.members_id)
#         self.assertNotEqual(getattr(member, "admin_notes"), "my note")

#     def test_members_profile_schema(self):
#         """Test that the schema for members registration is correct."""
#         res = self.client.get(PROFILE_SCHEMA_URL)
#         self.assertTrue("birthday" not in res.data)
#         self.assertEqual(res.data["first_name"]["read_only"], True)
#         self.assertEqual(res.data["first_name"]["required"], False)
#         self.assertEqual(res.data["address_street"]["required"], True)

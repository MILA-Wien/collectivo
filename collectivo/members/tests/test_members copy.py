"""Tests of the members API."""
from django.contrib.auth import get_user_model
from django.db.models import signals
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import localdate
from rest_framework.test import APIClient

from collectivo.utils.tests import create_testuser

from ..models import Member

User = get_user_model()

MEMBERS_URL = reverse("collectivo:collectivo.members:member-list")
MEMBER_URL_LABEL = "collectivo:collectivo.members:member-detail"
PROFILE_URL = reverse("collectivo:collectivo.members:profile")
REGISTER_URL = reverse("collectivo:collectivo.members:register")
REGISTRATION_SCHEMA_URL = reverse(
    "collectivo:collectivo.members:register-schema"
)
PROFILE_SCHEMA_URL = reverse("collectivo:collectivo.members:profile-schema")

TEST_MEMBER = {
    "first_name": "firstname",
    "last_name": "lastname",
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
    "membership_start": localdate(),
    "email": "some_member@example.com",
}

TEST_USER = {
    "email": "some_member@example.com",
    "username": "some_member@example.com",
    "firstName": "firstname",
    "lastName": "lastname",
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
        for i in [0, 2, 1]:
            user = User.objects.create_user(
                username=str(i),
                email=str(i) + "@example.com",
            )
            payload = {
                **TEST_MEMBER_POST,
                "user": user.id,
            }
            self.client.post(MEMBERS_URL, payload)

    def test_get_members(self):
        """Get the summary of members."""
        res = self.client.get(MEMBERS_URL)
        self.assertEqual(res.status_code, 200)

    def test_create_members(self):
        """Test that admins can create members."""
        self.create_members()
        self.assertEqual(len(Member.objects.all()), 3)


#     def test_update_member_admin_fields(self):
#         """Test that admins can write to admin fields."""
#         payload = {**TEST_MEMBER_POST, "email": "0@example.com"}
#         res1 = self.client.post(MEMBERS_CREATE_URL, payload)
#         self.assertEqual(res1.status_code, 201)

#         res2 = self.client.patch(
#             reverse(
#                 "collectivo:collectivo.members:member-detail",
#                 args=[res1.data["id"]],
#             ),
#             {"admin_notes": "my note"},
#         )
#         if res2.status_code != 200:
#             raise ValueError("API call failed: ", res2.content)
#         member = Member.objects.get(id=res1.data["id"])
#         self.assertEqual(getattr(member, "admin_notes"), "my note")

#     def test_member_sorting(self):
#         """Test that all member fields can be sorted."""
#         self.create_members()

#         res = self.client.get(MEMBERS_URL + "?ordering=first_name")
#         self.assertEqual(
#             [entry["first_name"] for entry in res.data], ["0", "1", "2"]
#         )

#         res = self.client.get(MEMBERS_URL + "?ordering=-first_name")
#         self.assertEqual(
#             [entry["first_name"] for entry in res.data], ["2", "1", "0"]
#         )

#     def test_member_filtering(self):
#         """Test that member names can be filtered with 'contains'."""
#         self.create_members()

#         res = self.client.get(MEMBERS_URL + "?first_name__contains=1")
#         self.assertEqual([entry["first_name"] for entry in res.data], ["1"])

#     def test_member_pagination(self):
#         """Test that pagination works for members."""
#         self.create_members()

#         limit = 3
#         offset = 5
#         res = self.client.get(MEMBERS_URL + f"?limit={limit}&offset={offset}")

#         self.assertEqual(
#             [m.id for m in Member.objects.all()][offset : offset + limit],
#             [m["id"] for m in res.data["results"]],
#         )

#     def test_register_member_assigns_members_user_role(self):
#         """Test that new members receive the auth role 'members_user'."""
#         # Create a new member
#         res = self.user_client.post(REGISTER_URL, TEST_MEMBER_POST)
#         self.assertEqual(res.status_code, 201)
#         _, data = self.get_token(self.user_email)
#         self.assertIn("members_user", data["realm_access"]["roles"])

#         # Delete the member again
#         res = self.client.delete(
#             reverse(MEMBER_URL_LABEL, args=[res.data["id"]])
#         )
#         self.assertEqual(res.status_code, 204)
#         _, data = self.get_token(self.user_email)
#         self.assertNotIn("members_user", data["realm_access"]["roles"])

#     def test_create_member_as_admin(self):
#         """Test that admins can create new member without keycloak."""
#         payload = {
#             **TEST_MEMBER_POST,
#             "email": "new_test_member@example.com",
#         }
#         res = self.client.post(MEMBERS_CREATE_URL, payload)
#         self.assertEqual(res.status_code, 201)
#         user_id = self.keycloak.get_user_id(payload["email"])
#         userinfo = self.keycloak.get_user(user_id)
#         self.assertEqual(userinfo["firstName"], payload["first_name"])
#         self.assertEqual(userinfo["emailVerified"], False)

# def test_register_member_assigns_members_user_role(self):
#     """Test that new members receive the auth role 'members_user'."""
#     # Create a new member
#     res = self.user_client.post(REGISTER_URL, TEST_MEMBER_POST)
#     self.assertEqual(res.status_code, 201)
#     _, data = self.get_token(self.user_email)
#     self.assertIn("members_user", data["realm_access"]["roles"])

#     # Delete the member again
#     res = self.client.delete(
#         reverse(MEMBER_URL_LABEL, args=[res.data["id"]])
#     )
#     self.assertEqual(res.status_code, 204)
#     _, data = self.get_token(self.user_email)
#     self.assertNotIn("members_user", data["realm_access"]["roles"])

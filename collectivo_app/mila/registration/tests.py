"""Tests of the members extension for users."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.memberships.models import MembershipStatus
from collectivo.profiles.models import UserProfile
from collectivo.tags.models import Tag
from collectivo.utils.test import create_testuser

from . import models

User = get_user_model()

REGISTER_URL = reverse("mila.registration:register")
REGISTER_SCHEMA_URL = reverse("mila.registration:register-schema")

TEST_USER = {
    "email": "some_member@example.com",
    "username": "some_member@example.com",
    "first_name": "firstname",
    "last_name": "lastname",
}


TEST_PROFILE = {
    "gender": "diverse",
    "address_street": "my street",
    "address_number": "1",
    "address_postcode": "0000",
    "address_city": "my city",
    "address_country": "my country",
}

PAYMENT_PROFILE = {
    "bank_account_owner": "my name",
    "bank_account_iban": "my iban",
    "payment_method": "sepa",
}

SURVEY_PROFILE = {
    "survey_contact": "my contact",
    "survey_motivation": "my motivation",
}

TEST_MEMBER_POST = {
    **TEST_USER,
    **TEST_PROFILE,
    **PAYMENT_PROFILE,
    **SURVEY_PROFILE,
    "person_type": "natural",
    "membership_type": "active",
    "shares_payment_type": "sepa",
    "statutes_approved": True,
    "shares_tarif": "normal",
}


class MilaRegistrationTests(TestCase):
    """Test the memberships extension for users."""

    def setUp(self):
        """Prepare client and create test user."""
        self.client = APIClient()
        self.user = create_testuser(TEST_USER)
        self.client.force_authenticate(self.user)
        self.skill = models.SurveySkill.objects.get_or_create(name="sk1")[0]
        self.group = models.SurveyGroup.objects.get_or_create(name="gr1")[0]
        self.status = MembershipStatus.objects.get_or_create(
            name="Investierend"
        )[0]

    def create_member(self, payload=TEST_MEMBER_POST):
        """Create a sample member."""
        res = self.client.post(
            REGISTER_URL,
            {
                **payload,
                "membership_status": self.status.id,
                "skills": [self.skill.id],
                "groups_interested": [self.group.id],
            },
        )
        self.assertEqual(res.status_code, 201)
        member = UserProfile.objects.get(user=res.data["user"])
        return member

    def test_create_member(self):
        """Test that an authenticated user can create itself as a member."""
        member = self.create_member()
        for key, value in TEST_PROFILE.items():
            self.assertEqual(value, getattr(member, key))

        membership = member.user.memberships.last()
        self.assertEqual(membership.status, self.status)
        self.assertEqual(membership.shares_signed, 9)

        # Automatically created payment profile
        paymentprofile = member.user.payment_profile
        for k, v in PAYMENT_PROFILE.items():
            self.assertEqual(v, getattr(paymentprofile, k))

        surveyprofile = member.user.registration_survey
        self.assertEqual(surveyprofile.skills.count(), 1)
        self.assertEqual(surveyprofile.skills.first(), self.skill)
        self.assertEqual(surveyprofile.groups_interested.count(), 1)
        self.assertEqual(surveyprofile.groups_interested.first(), self.group)
        for k, v in SURVEY_PROFILE.items():
            self.assertEqual(v, getattr(surveyprofile, k))

    def test_create_member_legal(self):
        """Test that a legal member automatically becomes type investing."""
        payload = {**TEST_MEMBER_POST, "person_type": "legal"}
        member = self.create_member(payload)

        memberships = member.user.memberships.all()
        self.assertEqual(len(memberships), 1)
        membership = memberships[0]
        self.assertEqual(membership.status, self.status)
        self.assertEqual(membership.shares_signed, 9)

    def test_tags_assigned(self):
        """Test that tags are assigned to the user when a member is created."""
        member = self.create_member()
        tag = Tag.objects.get_or_create(name="Satzung angenommen")[0]
        self.assertIn(tag, member.user.tags.all())
        tag = Tag.objects.get_or_create(name="Öffentliche Verwendung")[0]
        self.assertNotIn(tag, member.user.tags.all())

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

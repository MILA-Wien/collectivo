"""Tests for the schemas of the members extension."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.utils.test import create_testuser

User = get_user_model()

REGISTER_SCHEMA_URL = reverse("collectivo:collectivo.members:register-schema")
MEMBER_SCHEMA_URL = reverse("collectivo:collectivo.members:member-schema")


class MembersSchemaTests(TestCase):
    """Test the members schema."""

    def setUp(self):
        """Prepare client."""
        self.client = APIClient()
        self.user = create_testuser(superuser=True)
        self.client.force_authenticate(self.user)

    def test_member_schema(self):
        """Test member schema."""
        res = self.client.get(MEMBER_SCHEMA_URL)
        schema = res.data
        self.assertEqual(
            schema["user__tags"]["choices_url"], "/api/tags/tags/"
        )

    def test_registration_schema(self):
        """Test registration schema."""
        res = self.client.get(REGISTER_SCHEMA_URL)
        schema = res.data
        self.assertIn("condition", schema["legal_name"])

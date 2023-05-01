"""Tests of the profiles extension."""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.utils.test import create_testuser

from .models import UserProfile

PROFILE_URL = reverse("collectivo:collectivo.profiles:profile-self")
PROFILES_URL = reverse("collectivo:collectivo.profiles:profile-list")
PROFILE_SCHEMA_URL = reverse(
    "collectivo:collectivo.profiles:profile-self-schema"
)

TEST_USER = {
    "email": "some_member@example.com",
    "username": "some_member@example.com",
    "firstName": "firstname",
    "lastName": "lastname",
}

PROFILE = {
    "gender": "diverse",
    "address_street": "my street",
    "address_number": "1",
    "address_postcode": "0000",
    "address_city": "my city",
    "address_country": "my country",
    "person_type": "natural",
}


class ProfileSetupTests(TestCase):
    """Test that the extension is installed correctly."""

    def setUp(self):
        """Initialize testing instance."""
        self.extension = Extension.objects.get(name="memberships")

    def test_menu_items_exist(self):
        """Test that the menu items are registered."""
        res = MenuItem.objects.filter(extension=self.extension)
        self.assertEqual(len(res), 2)


class ProfileTests(TestCase):
    """Tests of the profiles extension."""

    def setUp(self):
        """Prepare test case."""
        self.client = APIClient()
        self.user = create_testuser(TEST_USER)
        self.client.force_authenticate(self.user)

    def test_profile_automatically_created(self):
        """Test that a profile is automatically created."""
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_get_profile(self):
        """Test that a member can view it's own data."""
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, 200)

    def test_get_other_user_profiles_fails(self):
        """Test that a member cannot view other members data."""
        res = self.client.get(PROFILES_URL)
        self.assertEqual(res.status_code, 403)

    def test_update_profile(self):
        """Test that a member can edit it's data."""
        self.client.patch(PROFILE_URL, PROFILE)
        res = self.client.get(PROFILE_URL)
        for key, value in PROFILE.items():
            self.assertEqual(str(value), str(res.data[key]))

    def test_update_profile_fails(self):
        """Test that a member cannot omit non-blank fields."""
        res = self.client.patch(PROFILE_URL, {**PROFILE, "address_street": ""})
        self.assertEqual(res.status_code, 400)

    def test_update_profile_admin_fields_fails(self):
        """Test that a member cannot edit admin fields of it's own data."""
        self.client.patch(PROFILE_URL, {"notes": "my note"})
        member = UserProfile.objects.get(user=self.user)
        self.assertNotEqual(getattr(member, "notes"), "my note")

    def test_schema(self):
        """Test that the schema for members registration is correct."""
        res = self.client.get(PROFILE_SCHEMA_URL)
        for c in [
            "birthday",
            "occupation",
            "legal_name",
            "legal_id",
            "legal_type",
        ]:
            self.assertTrue(c in res.data)
            self.assertTrue("condition" in res.data[c])
        self.assertEqual(res.data["address_street"]["required"], True)

"""Tests for the core extension."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.extensions.models import Extension
from collectivo.menus.models import Menu
from collectivo.utils.permissions import HasGroup, IsSuperuser
from collectivo.utils.test import create_testuser
from collectivo.version import __version__
from ..serializers import UserProfilesSerializer


"""Tests of the profiles extension."""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.utils.test import create_testuser


PROFILES_URL = reverse("collectivo:collectivo.core:users-extended-list")


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
        self.user = create_testuser(superuser=True)
        self.client.force_authenticate(self.user)

    def test_get_profile(self):
        """Test that a member can view it's own data."""
        res = self.client.get(PROFILES_URL)
        self.assertEqual(res.status_code, 200)
        print(res.data)


class CoreSetupTests(TestCase):
    """Test extension is registered correctly."""

    def test_default_menus(self):
        """Test default menus exist."""
        user = get_user_model().objects.all().first()
        serializer = UserProfilesSerializer(user)
        # print(serializer.get_fields())
        # print(UserProfilesSerializer.profile__phone)

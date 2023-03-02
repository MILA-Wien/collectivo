"""Tests of the members extension."""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.dashboard.models import DashboardTile
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.users.models import User
from collectivo.users.tests.utils import create_test_user

TILES_URL = reverse("collectivo:collectivo.dashboard:tile-list")
MENUS_URL = reverse("collectivo:collectivo.menus:menu-list")


class MembersExtensionTests(TestCase):
    """Test that the extension is installed correctly."""

    def setUp(self):
        """Initialize testing instance."""
        self.client = AuthClient()
        self.extension = Extension.objects.get(name="collectivo.members")

    def tearDown(self) -> None:
        if hasattr(self, "user"):
            self.user.delete()

    def test_menu_items_exist(self):
        """Test that the menu items are registered."""
        res = MenuItem.objects.filter(extension=self.extension)
        self.assertEqual(len(res), 3)

    def test_tile_exist(self):
        """Test that the menu items are registered."""
        res = DashboardTile.objects.filter(extension=self.extension)
        self.assertEqual(len(res), 1)

    def test_profile_menu_item(self):
        """Test that the menu items are registered."""
        self.user = create_test_user(roles=["members_user"])
        self.client.force_authenticate(self.user)
        items = [
            i["name"] for i in self.client.get(MENUS_URL).data[0]["items"]
        ]
        print(items)

    def test_tile_not_blocked(self):
        """Test tile should appear for user without blocked role."""
        self.user = create_test_user(roles=[])
        self.client.force_authenticate(self.user)
        items = [i["name"] for i in self.client.get(TILES_URL).data]
        self.assertTrue("members_registration_tile" in items)

    def test_tile_blocked(self):
        """Test tile should not appear for user with blocked role."""
        self.user = create_test_user(roles=["members_user"])
        self.client.force_authenticate(self.user)
        items = [i["name"] for i in self.client.get(TILES_URL).data]
        self.assertFalse("members_registration_tile" in items)

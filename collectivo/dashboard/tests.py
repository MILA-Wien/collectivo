"""Tests of the members API."""
from django.test import TestCase
from django.urls import reverse

from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.users.clients import AuthClient

from .models import DashboardTile

TILES_URL = reverse("collectivo:collectivo.dashboard:tile-list")
EXTENSIONS_URL = reverse("collectivo:collectivo.extensions:extension-list")
EXTENSION_NAME = "dashboard"


class DashboardSetupTests(TestCase):
    """Test that the dashboard extension is installed correctly."""

    def test_extension_exists(self):
        """Test that the extension is automatically registered."""
        exists = Extension.objects.filter(name=EXTENSION_NAME).exists()
        self.assertTrue(exists)

    def test_menu_items_exist(self):
        """Test that the menu items are registered."""
        res = MenuItem.objects.filter(extension__name=EXTENSION_NAME)
        self.assertEqual(len(res), 1)


class DashboardPublicAPITests(TestCase):
    """Test the dashboard API available to public."""

    def setUp(self):
        """Prepare test case."""
        self.client = AuthClient()

    def test_access_menu_api_fails(self):
        """Test that menu API cannot be accessed by a public user."""
        res = self.client.get(TILES_URL)
        self.assertEqual(res.status_code, 403)


class DashboardPrivateAPITests(TestCase):
    """Test the dashboard API available to users."""

    def setUp(self):
        """Prepare test case."""
        self.client = AuthClient.as_pseudo_user()

    def test_get_tile_fails(self):
        """Test that users can view tiles."""
        res = self.client.get(TILES_URL)
        self.assertEqual(res.status_code, 200)

    def test_post_tile_fails(self):
        """Test users cannot edit tiles."""
        res = self.client.post(TILES_URL)
        self.assertEqual(res.status_code, 403)


class DashboardAPITests(TestCase):
    """Test the dashboard API available to admins."""

    def setUp(self):
        """Prepare test case."""
        # Set up client with authenticated user
        self.client = AuthClient.as_pseudo_user(
            roles=["superuser", "test_role", "test_role2"]
        )

        # Register a test extension
        self.ext_name = "my_extension"
        self.client.post(EXTENSIONS_URL, {"name": self.ext_name})

        # Define payload for dashboard tile
        self.tile = {
            "name": "my_tile",
            "extension": self.ext_name,
            "component_name": "test_component",
        }

    def test_create_tile(self):
        """Test creating tile succeeded."""
        DashboardTile.register(**self.tile)
        tile = DashboardTile.objects.filter(name=self.tile["name"])
        self.assertTrue(tile.exists())

    def test_tile_correct_role(self):
        """Test tile should appear for user with required role."""
        DashboardTile.register(**self.tile, required_role="test_role")
        res = self.client.get(TILES_URL)
        items = [i["name"] for i in res.data]
        self.assertTrue("my_tile" in items)

    def test_tile_wrong_role(self):
        """Test menuitem should not appear for user without required role."""
        DashboardTile.register(**self.tile, required_role="wrong_role")
        res = self.client.get(TILES_URL)
        items = [i["name"] for i in res.data]
        self.assertFalse("my_tile" in items)

    def test_tile_blocked_role(self):
        """Test menuitem should not appear for user with blocked role."""
        DashboardTile.register(**self.tile, blocked_role="test_role")
        res = self.client.get(TILES_URL)
        items = [i["name"] for i in res.data]
        self.assertFalse("my_tile" in items)

    def test_tile_blocked_role_2(self):
        """Test menuitem should not appear for user with blocked role."""
        DashboardTile.register(
            **self.tile, blocked_role="test_role", required_role="test_role2"
        )
        res = self.client.get(TILES_URL)
        items = [i["name"] for i in res.data]
        self.assertFalse("my_tile" in items)

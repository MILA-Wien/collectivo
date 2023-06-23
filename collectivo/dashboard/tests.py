"""Tests of the members API."""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.core.models import Permission, PermissionGroup
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.utils.test import create_testuser

from .models import DashboardTile

TILES_URL = reverse("collectivo.dashboard:tile-self")
TILES_ADMIN_URL_PATH = "collectivo.dashboard:tile-detail"
EXTENSIONS_URL = reverse("collectivo.extensions:extension-list")
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
        self.assertEqual(len(res), 2)


class DashboardPublicAPITests(TestCase):
    """Test the dashboard API available to public."""

    def setUp(self):
        """Prepare test case."""
        self.client = APIClient()

    def test_access_menu_api_fails(self):
        """Test that menu API cannot be accessed by a public user."""
        res = self.client.get(TILES_URL)
        self.assertEqual(res.status_code, 401)


class DashboardPrivateAPITests(TestCase):
    """Test the dashboard API available to users."""

    def setUp(self):
        """Prepare test case."""
        self.client = APIClient()
        self.user = create_testuser()
        self.client.force_authenticate(self.user)

    def test_get_tile_fails(self):
        """Test that users can view tiles."""
        res = self.client.get(TILES_URL)
        self.assertEqual(res.status_code, 200)

    def test_post_tile_fails(self):
        """Test users cannot edit tiles."""
        res = self.client.post(TILES_URL)
        self.assertEqual(res.status_code, 405)


class DashboardAPITests(TestCase):
    """Test the dashboard API available to admins."""

    def setUp(self):
        """Prepare test case."""
        # Set up client with authenticated user
        self.client = APIClient()
        self.user = create_testuser(
            perms=["test_perm", "test_perm2"],
            superuser=True,
        )
        self.client.force_authenticate(self.user)
        self.test_group = PermissionGroup.objects.get_or_create(
            name="test_group"
        )[0]
        self.perm = Permission.objects.get_or_create(name="test_perm")[0]
        self.test_group.permissions.add(self.perm)
        self.test_group.save()
        self.wrong_perm = Permission.objects.get_or_create(name="wrong_perm")[
            0
        ]
        # Register a test extension
        self.ext_name = "my_extension"
        self.client.post(EXTENSIONS_URL, {"name": self.ext_name})

        # Define payload for dashboard tile
        self.tile = {
            "name": "my_tile",
            "extension": self.ext_name,
            "source": "component",
            "component_name": "test_component",
        }

    def test_create_tile(self):
        """Test creating tile succeeded."""
        DashboardTile.objects.register(**self.tile)
        tile = DashboardTile.objects.filter(name=self.tile["name"])
        self.assertTrue(tile.exists())

    def test_tile_correct_role(self):
        """Test tile should appear for user with required permission."""
        DashboardTile.objects.register(**self.tile, requires_perm=self.perm)
        res = self.client.get(TILES_URL)
        items = [i["name"] for i in res.data]
        self.assertTrue("my_tile" in items)

    def test_tile_wrong_role(self):
        """Test menuitem should not appear for user without required role."""
        DashboardTile.objects.register(
            **self.tile, requires_perm=self.wrong_perm
        )
        res = self.client.get(TILES_URL)
        items = [i["name"] for i in res.data]
        self.assertFalse("my_tile" in items)

    def test_tile_not_active(self):
        """Test tile should not appear if not active."""
        DashboardTile.objects.register(**self.tile, active=False)
        res = self.client.get(TILES_URL)
        items = [i["name"] for i in res.data]
        self.assertFalse("my_tile" in items)

    def test_tile_templating(self):
        """Test that django templating language can be used in tile."""
        DashboardTile.objects.create(
            name="my_custom_tile",
            source="db",
            content="Hello {{user.username}}",
            order=-9999,
        )
        res = self.client.get(TILES_URL)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data[0]["content"], "Hello testuser")

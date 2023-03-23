"""Test the menus extension."""
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.extensions.models import Extension
from collectivo.menus.models import Menu, MenuItem
from collectivo.utils.test import create_testuser

EXTENSIONS_URL = reverse("collectivo:collectivo.extensions:extension-list")
MENUS_URL = reverse("collectivo:collectivo.menus:menu-list")
ITEMS_URL = reverse("collectivo:collectivo.menus:menuitem-list")


class MenusSetupTests(TestCase):
    """Test that the extension is installed correctly."""

    def setUp(self):
        """Initialize testing instance."""
        self.name = "menus"

    def test_extension_exists(self):
        """Test that the extension is registered."""
        exists = Extension.objects.filter(name=self.name).exists()
        self.assertTrue(exists)


class MenusAPITests(TestCase):
    """Test the menus API."""

    def setUp(self):
        """Prepare test case."""
        self.client = APIClient()
        self.user = create_testuser(superuser=True)
        self.extension = Extension.objects.get(name="menus")

        test_menu = Menu.register(
            name="test_menu",
            extension=self.extension,
        )

        for order in [3, 1, 2]:
            MenuItem.register(
                name=f"test_item_{order}",
                label=f"Test Item {order}",
                extension=self.extension,
                parent=test_menu,
                order=order,
            )

        self.group = Group.objects.get_or_create(name="test_group")[0]

        MenuItem.register(
            name="test_item_4",
            label="Test Item 4",
            extension=self.extension,
            parent=test_menu,
            order=4,
            requires_group=self.group,
        )

        self.menu_url = reverse(
            "collectivo:collectivo.menus:menu-detail",
            kwargs={"extension": self.extension.name, "menu": test_menu.name},
        )

    def test_get_menu_succeeds(self):
        """Test that menu is returned."""
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.menu_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["name"], "test_menu")

    def test_get_menu_fails(self):
        """Test that menu API cannot be accessed by public user."""
        self.client.force_authenticate(user=None)
        res = self.client.get(MENUS_URL)
        self.assertEqual(res.status_code, 401)
        res = self.client.get(ITEMS_URL)
        self.assertEqual(res.status_code, 401)

    def test_menu_item_order(self):
        """Test that menu items are returned in correct order."""
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.menu_url)
        items = [item["name"] for item in res.data["items"]]
        self.assertEqual(items, [f"test_item_{order}" for order in [1, 2, 3]])

    def test_menu_item_correct_group(self):
        """Test menuitem should appear only if user has required group."""
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.menu_url)
        items = [item["name"] for item in res.data["items"]]
        self.assertFalse("test_item_4" in items)
        self.user.groups.add(self.group)
        res = self.client.get(self.menu_url)
        items = [item["name"] for item in res.data["items"]]
        self.assertTrue("test_item_4" in items)

"""Test the menus extension."""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.extensions.models import Extension
from collectivo.menus.models import Menu, MenuItem

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
        self.client = AuthClient().as_superuser()
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
                menu=test_menu,
                order=order,
            )

        MenuItem.register(
            name="test_item_4",
            label="Test Item 4",
            extension=self.extension,
            menu=test_menu,
            order=4,
            required_role="test_role",
        )

        self.menu_url = reverse(
            "collectivo:collectivo.menus:menu-detail",
            kwargs={"extension": self.extension.name, "menu": test_menu.name},
        )

    def test_get_menu_succeeds(self):
        """Test that menu is returned."""
        res = self.client.get(self.menu_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["name"], "test_menu")

    def test_get_menu_fails(self):
        """Test that menu API cannot be accessed by public user."""
        self.client = AuthClient()
        res = self.client.get(MENUS_URL)
        self.assertEqual(res.status_code, 403)
        res = self.client.get(ITEMS_URL)
        self.assertEqual(res.status_code, 403)

    def test_menu_item_order(self):
        """Test that menu items are returned in correct order."""
        res = self.client.get(self.menu_url)
        items = [item["name"] for item in res.data["items"]]
        self.assertEqual(items, [f"test_item_{order}" for order in [1, 2, 3]])

    def test_menu_item_correct_role(self):
        """Test menuitem should appear for user with correct role."""
        res = self.client.get(self.menu_url)
        items = [item["name"] for item in res.data["items"]]
        self.assertFalse("test_item_4" in items)

        self.client = AuthClient().as_pseudo_user(roles=["test_role"])
        res = self.client.get(self.menu_url)
        items = [item["name"] for item in res.data["items"]]
        self.assertTrue("test_item_4" in items)

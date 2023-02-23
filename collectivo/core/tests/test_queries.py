"""Test the features of the menu API."""
from django.test import TestCase
from django.urls import reverse
from ..utils import register_menuitem
from collectivo.menus.models import Menu, MenuItem
from collectivo.users.clients import AuthClient
from collectivo.users.userinfo import UserInfo


# EXTENSIONS_URL = reverse("collectivo:collectivo.extensions:extension-list")
# MENUS_URL = reverse("collectivo:collectivo.menus:menu-list")
# ITEMS_URL = reverse(
#     "collectivo:collectivo.menus:menuitem-list",
#     kwargs={"menu_id": "main_menu"},
# )


class PublicMenusApiTests(TestCase):
    """Test the publicly available menus API."""

    def setUp(self):
        """Prepare test case."""
        self.client = AuthClient()
        self.client.force_authenticate()

    def test_access_menu_api_fails(self):
        """Test that menu API cannot be accessed by public user."""
        res = self.client.get(
            reverse(
                "collectivo:collectivo.menus:menu-list",
            )
            + "?extension=collectivo.menus&menu=main_menu"
        )
        print(res.content)

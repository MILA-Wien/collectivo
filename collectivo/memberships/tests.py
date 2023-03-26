"""Tests of the memberships extension."""
from django.contrib.auth import get_user_model
from django.test import TestCase

from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem

User = get_user_model()


class MembersSetupTests(TestCase):
    """Test that the extension is installed correctly."""

    def setUp(self):
        """Initialize testing instance."""
        self.extension = Extension.objects.get(name="memberships")

    def test_menu_items_exist(self):
        """Test that the menu items are registered."""
        res = MenuItem.objects.filter(extension=self.extension)
        self.assertEqual(len(res), 2)

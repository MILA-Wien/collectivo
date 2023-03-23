"""Tests of the members extensions' setup function."""
from django.test import TestCase

from collectivo.dashboard.models import DashboardTile
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem


class MembersSetupTests(TestCase):
    """Test that the extension is installed correctly."""

    def setUp(self):
        """Initialize testing instance."""
        self.extension = Extension.objects.get(name="members")

    def test_menu_items_exist(self):
        """Test that the menu items are registered."""
        res = MenuItem.objects.filter(extension=self.extension)
        self.assertEqual(len(res), 2)

    def test_tile_exist(self):
        """Test that the menu items are registered."""
        res = DashboardTile.objects.filter(extension=self.extension)
        self.assertEqual(len(res), 1)

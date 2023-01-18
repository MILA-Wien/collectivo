"""Tests of the members extension."""
from django.test import TestCase
from django.urls import reverse
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.dashboard.models import DashboardTile
from collectivo.auth.userinfo import UserInfo
from collectivo.auth.clients import CollectivoAPIClient


TILES_URL = reverse('collectivo:collectivo.dashboard:tile-list')


class MembersRegistrationTests(TestCase):
    """Test that the extension is installed correctly."""

    def setUp(self):
        """Initialize testing instance."""
        self.name = 'members'
        self.client = CollectivoAPIClient()

    def test_extension_exists(self):
        """Test that the extension is automatically registered."""
        exists = Extension.objects.filter(name=self.name).exists()
        self.assertTrue(exists)

    def test_menu_items_exist(self):
        """Test that the menu items are registered."""
        res = MenuItem.objects.filter(extension=self.name)
        self.assertEqual(len(res), 3)

    def test_tile_exist(self):
        """Test that the menu items are registered."""
        res = DashboardTile.objects.filter(extension=self.name)
        self.assertEqual(len(res), 1)

    def test_tile_not_blocked(self):
        """Test tile should appear for user without blocked role."""
        user = UserInfo(is_authenticated=True)
        self.client.force_authenticate(user)
        res = self.client.get(TILES_URL)
        items = [i['tile_id'] for i in res.data]
        self.assertTrue('members_registration_tile' in items)

    def test_tile_blocked(self):
        """Test menuitem should not appear for user with blocked role."""
        user = UserInfo(is_authenticated=True, roles=['members_user'])
        self.client.force_authenticate(user)
        res = self.client.get(TILES_URL)
        items = [i['tile_id'] for i in res.data]
        self.assertFalse('members_registration_tile' in items)

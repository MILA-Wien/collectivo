"""Tests of the members API."""
from django.test import TestCase
from django.urls import reverse
from collectivo.extensions.models import Extension
from collectivo.auth.clients import CollectivoAPIClient
from collectivo.auth.userinfo import UserInfo
from collectivo.menus.models import MenuItem
from .models import DashboardTile
from .utils import register_tile


TILES_URL = reverse('collectivo:collectivo.dashboard:tile-list')
EXTENSIONS_URL = reverse('collectivo:collectivo.extensions:extension-list')
EXTENSION_NAME = 'dashboard'


class DashboardRegistrationTests(TestCase):
    """Test that the dashboard extension is installed correctly."""

    def test_extension_exists(self):
        """Test that the extension is automatically registered."""
        exists = Extension.objects.filter(name=EXTENSION_NAME).exists()
        self.assertTrue(exists)

    def test_menu_items_exist(self):
        """Test that the menu items are registered."""
        res = MenuItem.objects.filter(extension=EXTENSION_NAME)
        self.assertEqual(len(res), 1)


class PublicDashboardApiTests(TestCase):
    """Test the dashboard API available to public."""

    def setUp(self):
        """Prepare test case."""
        self.client = CollectivoAPIClient()

    def test_access_menu_api_fails(self):
        """Test that menu API cannot be accessed by public user."""
        res = self.client.get(TILES_URL)
        self.assertEqual(res.status_code, 403)


class PrivateDashboardApiTests(TestCase):
    """Test the dashboard API available to users."""

    def setUp(self):
        """Prepare test case."""
        self.client = CollectivoAPIClient()
        self.client.force_authenticate(UserInfo(is_authenticated=True))

    def test_get_tile_fails(self):
        """Test that users can view tiles."""
        res = self.client.get(TILES_URL)
        self.assertEqual(res.status_code, 200)

    def test_post_tile_fails(self):
        """Test users cannot edit tiles."""
        res = self.client.post(TILES_URL)
        self.assertEqual(res.status_code, 403)


class AdminMenusApiTests(TestCase):
    """Test the dashboard API available to admins."""

    def setUp(self):
        """Prepare test case."""
        # Set up client with authenticated user
        self.client = CollectivoAPIClient()
        user = UserInfo(
            user_id='ac4339c5-56f6-4df5-a6c8-bcdd3683a56a',
            roles=['superuser', 'test_role', 'test_role2'],
            email='test_member_1@example.com',
            is_authenticated=True
        )
        self.client.force_authenticate(user)

        # Register a test extension
        self.ext_name = 'my_extension'
        self.client.post(EXTENSIONS_URL, {'name': self.ext_name})

        # Define payloads for API calls
        self.tile = {
            'tile_id': 'my_tile',
            'extension': self.ext_name,
            'component_name': 'test_component',
        }

    def test_create_tile(self):
        """Test creating tile succeeded."""
        self.client.post(TILES_URL, self.tile)
        tile = DashboardTile.objects.filter(tile_id=self.tile['tile_id'])
        self.assertTrue(tile.exists())

    def test_tile_correct_role(self):
        """Test tile should appear for user with required role."""
        payload = {**self.tile, 'required_role': 'test_role'}
        self.client.post(TILES_URL, payload)
        res = self.client.get(TILES_URL, payload)
        items = [i['tile_id'] for i in res.data]
        self.assertTrue('my_tile' in items)

    def test_tile_wrong_role(self):
        """Test menuitem should not appear for user without required role."""
        payload = {**self.tile, 'required_role': 'wrong_role'}
        self.client.post(TILES_URL, payload)
        res = self.client.get(TILES_URL, payload)
        items = [i['tile_id'] for i in res.data]
        self.assertFalse('my_tile' in items)

    def test_tile_blocked_role(self):
        """Test menuitem should not appear for user with blocked role."""
        payload = {**self.tile, 'blocked_role': 'test_role'}
        self.client.post(TILES_URL, payload)
        res = self.client.get(TILES_URL, payload)
        items = [i['tile_id'] for i in res.data]
        self.assertFalse('my_tile' in items)

    def test_tile_blocked_role_2(self):
        """Test menuitem should not appear for user with blocked role."""
        payload = {
            **self.tile,
            'blocked_role': 'test_role',
            'required_role': 'test_role2'}
        self.client.post(TILES_URL, payload)
        res = self.client.get(TILES_URL, payload)
        items = [i['tile_id'] for i in res.data]
        self.assertFalse('my_tile' in items)

    def test_create_tile_util(self):
        """Test creating tile with utils."""
        register_tile(**self.tile)
        tile = DashboardTile.objects.filter(tile_id=self.tile['tile_id'])
        self.assertTrue(tile.exists())

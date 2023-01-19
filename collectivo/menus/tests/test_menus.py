"""Test the features of the menu API."""
from django.test import TestCase
from django.urls import reverse
from ..utils import register_menuitem
from collectivo.menus.models import Menu, MenuItem
from collectivo.auth.clients import CollectivoAPIClient
from collectivo.auth.userinfo import UserInfo


EXTENSIONS_URL = reverse('collectivo:collectivo.extensions:extension-list')
MENUS_URL = reverse('collectivo:collectivo.menus:menu-list')
ITEMS_URL = reverse('collectivo:collectivo.menus:menuitem-list',
                    kwargs={'menu_id': 'main_menu'})


class MenusRegistrationTests(TestCase):
    """Test that menu items of the extension are registered correctly."""

    def test_default_menus(self):
        """Test default menus exist."""
        default_menus = ['main_menu', 'admin_menu']
        for menu in default_menus:
            self.assertTrue(Menu.objects.filter(menu_id=menu).exists())


class PublicMenusApiTests(TestCase):
    """Test the publicly available menus API."""

    def setUp(self):
        """Prepare test case."""
        self.client = CollectivoAPIClient()

    def test_access_menu_api_fails(self):
        """Test that menu API cannot be accessed by public user."""
        res = self.client.get(MENUS_URL)
        self.assertEqual(res.status_code, 403)
        res = self.client.get(ITEMS_URL)
        self.assertEqual(res.status_code, 403)


class PrivateMenusApiTests(TestCase):
    """Test the privatly available menus API."""

    def setUp(self):
        """Prepare test case."""
        self.client = CollectivoAPIClient()
        self.client.force_authenticate(UserInfo(is_authenticated=True))

    def test_access_menu_api(self):
        """Test that menu API can be accessed by authenticated user."""
        res = self.client.get(MENUS_URL)
        self.assertEqual(res.status_code, 200)
        res = self.client.get(ITEMS_URL)
        self.assertEqual(res.status_code, 200)


class AdminMenusApiTests(TestCase):
    """Test the publicly available menus API."""

    def setUp(self):
        """Prepare test case."""
        # Set up client with authenticated user
        self.client = CollectivoAPIClient()
        user = UserInfo(
            user_id='ac4339c5-56f6-4df5-a6c8-bcdd3683a56a',
            roles=['superuser', 'test_role'],
            email='test_member_1@example.com',
            is_authenticated=True
        )
        self.client.force_authenticate(user)

        # Register a test extension
        self.ext_name = 'my_extension'
        self.client.post(EXTENSIONS_URL, {'name': self.ext_name})

        # Define payloads for API calls
        self.menu = {
            'menu_id': 'my_menu',
            'extension': self.ext_name,
        }
        self.menu_item = {
            'item_id': 'my_menu_item',
            'menu_id': 'main_menu',
            'label': 'My menu item',
            'extension': self.ext_name,
        }

    def test_create_menu(self):
        """Test creating menu."""
        self.client.post(MENUS_URL, self.menu)
        exists = Menu.objects.filter(menu_id='my_menu').exists()
        self.assertTrue(exists)

    def test_create_menu_item(self):
        """Test creating item for a menu."""
        self.client.post(ITEMS_URL, self.menu_item)
        exists = MenuItem.objects.filter(item_id='my_menu_item').exists()
        self.assertTrue(exists)

    def test_menu_item_order(self):
        """Test that menu items are returned in correct order."""
        for order in [3, 1, 2]:
            payload = {**self.menu_item, 'order': order, 'item_id': order}
            res = self.client.post(ITEMS_URL, payload)
        res = self.client.get(ITEMS_URL)
        ids = [
            item['item_id'] for item in res.data
            if item['item_id'] in '123'
        ]
        self.assertEqual(ids, ['1', '2', '3'])

    def test_menu_item_correct_role(self):
        """Test menuitem should appear for user with correct role."""
        payload = {**self.menu_item, 'required_role': 'test_role'}
        self.client.post(ITEMS_URL, payload)
        res = self.client.get(ITEMS_URL, payload)
        items = [i['item_id'] for i in res.data]
        self.assertTrue('my_menu_item' in items)

    def test_menu_item_wrong_role(self):
        """Test menuitem should not appear for user with wrong role."""
        payload = {**self.menu_item, 'required_role': 'wrong_role'}
        self.client.post(ITEMS_URL, payload)
        res = self.client.get(ITEMS_URL, payload)
        items = [i['item_id'] for i in res.data]
        self.assertFalse('my_menu_item' in items)

    def test_create_menu_item_util(self):
        """Test creating item for a menu with utils."""
        payload = {**self.menu_item, 'label': 'My menu item1'}
        register_menuitem(**payload)
        item = MenuItem.objects.get(item_id='my_menu_item')
        self.assertTrue(item.label == 'My menu item1')
        payload = {**self.menu_item, 'label': 'My menu item2'}
        register_menuitem(**payload)
        item = MenuItem.objects.get(item_id='my_menu_item')
        self.assertTrue(item.label == 'My menu item2')

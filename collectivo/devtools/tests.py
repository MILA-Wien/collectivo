"""Tests of the devtools extension."""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from collectivo.menus.models import MenuItem
from collectivo.members.models import Member
from collectivo.extensions.models import Extension
from collectivo.utils import get_auth_manager
from .populate import members, users, superusers

EXTENSIONS_URL = reverse('collectivo:collectivo.extensions:extension-list')
MENUS_URL = reverse('collectivo:collectivo.menus:menu-list')
ITEMS_URL = reverse('collectivo:collectivo.menus:menuitem-list',
                    kwargs={'menu_id': 'main_menu'})


class TestExtensionRegistrationTests(TestCase):
    """Test the publicly available menus API."""

    def setUp(self):
        """Prepare client."""
        self.client = APIClient()
        self.auth_manager = get_auth_manager()
        self.name = 'devtools'

    def test_extension_exists(self):
        """Test extension exists."""
        extensions = Extension.objects.filter(name=self.name)
        self.assertTrue(extensions.exists())

    def test_default_menus(self):
        """Test menu items exist."""
        items = MenuItem.objects.filter(extension=self.name)
        self.assertEqual(len(items), 3)

    def test_test_members_exist(self):
        """Test that test users exist."""
        for user in users:
            user_id = self.auth_manager.get_user_id(user['email'])
            roles = self.auth_manager.get_realm_roles_of_user(user_id)
            roles = [role['name'] for role in roles]

            if user in members:
                self.assertTrue(
                    Member.objects.filter(email=user['email']).exists())
                self.assertTrue('members_user' in roles)

            if user in superusers:
                self.assertTrue('superuser' in roles)

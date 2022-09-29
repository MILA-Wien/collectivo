"""This module defines tests for the extensions app."""
from django.test import TestCase, modify_settings
from django.urls import reverse
from rest_framework.test import APIClient
from importlib import reload
import sys
# from rest_framework import status
from extensions.extension_manager import extension_manager


# Name of test extension
test_ext = 'extensions.tests.test_extension'


class ExtensionManagerTests(TestCase):
    """Tests for the global instance of extension_manager."""

    @modify_settings(INSTALLED_APPS={"append": test_ext})
    def test_installed_extension_is_registered(self):
        """Test that an installed extension is registered."""
        reload(sys.modules['extensions.extension_manager'])
        from extensions.extension_manager import extension_manager
        self.assertIn(test_ext, extension_manager.extensions.keys())

    def test_uninstalled_extension_is_not_registered(self):
        """Test that an uninstalled extension is not registered."""
        reload(sys.modules['extensions.extension_manager'])
        from extensions.extension_manager import extension_manager
        self.assertNotIn(test_ext, extension_manager.extensions.keys())


class PublicExtensionsApiTests(TestCase):
    """Test the public features of the extensions API."""

    def setUp(self):
        """Set up the test client."""
        self.client = APIClient()

    def test_GetExtensions(self):
        """Test getting list of installed extensions."""
        res = self.client.get(reverse('extensions:extensions'))
        self.assertEqual(list(extension_manager.extensions.keys()),
                         res.data['extensions'])

    # This test does not work as the modify_settings does not seem to work
    # @modify_settings(INSTALLED_APPS={"append": test_ext})
    # def test_extension_generates_API_endpoint(self):
    #     """Test that an extension can generate an API endpoint."""
    #     #reload(sys.modules['extensions.extension_manager'])
    #     #reload(sys.modules['collectivo.urls'])
    #     #reload(sys.modules['django.urls.resolvers'])
    #     #reload(sys.modules['django.urls.base'])

    #     url = reverse(f'{test_ext}:test_view')
    #     self.assertEqual(url, '/api/test_extension/')
    #     res = self.client.get(url)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)

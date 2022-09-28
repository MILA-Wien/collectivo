"""This module defines tests for the extensions app."""
from django.test import TestCase, modify_settings
from django.urls import reverse
from rest_framework.test import APIClient
from importlib import reload
import sys


# Name of an extension module for testing
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

    @modify_settings(INSTALLED_APPS={"append": test_ext})
    def testGetExtensions(self):
        """Test getting list of installed extensions."""
        from extensions.extension_manager import extension_manager
        self.client = APIClient()
        res = self.client.get(reverse('extensions:extensions'))
        self.assertEqual(list(extension_manager.extensions.keys()),
                         res.data['extensions'])

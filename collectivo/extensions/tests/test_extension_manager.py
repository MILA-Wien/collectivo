"""
This module defines tests for the extensions app.

Still missing: automatic API url registration
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from importlib import reload
import sys
from rest_framework import status
from extensions.extension_manager import extension_manager


class ExtensionManagerTests(TestCase):
    """Tests for the global instance of extension_manager."""

    def test_extension_is_registered(self):
        """Test that an installed extension is registered."""
        reload(sys.modules['extensions.extension_manager'])
        self.assertIn('test_extension', extension_manager.extensions.keys())


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

    def test_extension_generates_API_endpoint(self):
        """Test that an extension can generate an API endpoint."""
        url = reverse('test_extension:test_view')
        self.assertEqual(url, '/api/test_extension/')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

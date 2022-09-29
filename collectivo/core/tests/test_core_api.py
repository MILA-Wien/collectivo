"""Tests for the core API."""

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from core.version import __version__


class PublicCoreApiTests(TestCase):
    """Test the public features of the core API."""

    def setUp(self):
        """Set up the test client."""
        self.client = APIClient()

    def testGetVersion(self):
        """Test getting current version is correct."""
        res = self.client.get(reverse('core:version'))
        self.assertEqual(res.data['version'], __version__)

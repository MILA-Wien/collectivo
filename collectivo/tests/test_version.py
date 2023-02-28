"""Tests for the core API."""
from django.test import TestCase
from django.urls import reverse

from collectivo.users.clients import AuthClient
from collectivo.version import __version__


class PublicCoreApiTests(TestCase):
    """Test the public features of the core API."""

    def setUp(self):
        """Set up the test client."""
        self.client = AuthClient.as_superuser()

    def testGetVersion(self):
        """Test getting current version is correct."""
        res = self.client.get(reverse("collectivo:version"))
        self.assertEqual(res.data["version"], __version__)

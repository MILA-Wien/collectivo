"""Tests for the core extension."""
from django.test import TestCase
from django.urls import reverse

from collectivo.extensions.models import Extension
from collectivo.menus.models import Menu
from collectivo.users.clients import AuthClient
from collectivo.version import __version__


class CoreSetupTests(TestCase):
    """Test extension is registered correctly."""

    def test_default_menus(self):
        """Test default menus exist."""
        extension = Extension.objects.get(name="core")
        for name in ["main", "admin"]:
            self.assertTrue(
                Menu.objects.filter(extension=extension, name=name).exists()
            )


class CoreApiTests(TestCase):
    """Test the core API."""

    def setUp(self):
        """Set up the test client."""
        self.client = AuthClient.as_superuser()

    def testGetVersion(self):
        """Test getting current version is correct."""
        res = self.client.get(reverse("collectivo:collectivo.core:version"))
        self.assertEqual(res.data["version"], __version__)

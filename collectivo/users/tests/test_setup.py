"""Tests of the users extension."""
from django.test import TestCase

from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem


class UsersSetupTests(TestCase):
    """Test that the extension is installed correctly."""

    def setUp(self):
        """Initialize testing instance."""
        self.name = "users"

    def test_extension_exists(self):
        """Test that the extension is registered."""
        exists = Extension.objects.filter(name=self.name).exists()
        self.assertTrue(exists)

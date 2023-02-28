"""Tests for the core extension."""
from django.test import TestCase

from collectivo.extensions.models import Extension
from collectivo.menus.models import Menu


class CoreSetupTests(TestCase):
    """Test that extension is registered correctly."""

    def test_default_menus(self):
        """Test default menus exist."""
        extension = Extension.objects.get(name="core")
        for name in ["main", "admin"]:
            self.assertTrue(
                Menu.objects.filter(extension=extension, name=name).exists()
            )

"""Tests of the extensions module."""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.utils.test import create_testuser

from .models import Extension

EXTENSIONS_URL = reverse("collectivo:collectivo.extensions:extension-list")


class ExtensionsTests(TestCase):
    """Test the extensions extension."""

    def setUp(self):
        """Prepare test case."""
        self.client = APIClient()
        self.user = create_testuser(superuser=True)
        self.client.force_authenticate(self.user)
        self.name = "my_extension"
        Extension.objects.create(name=self.name)

    def test_list_extensions(self):
        """Test that extensions can be listed."""
        res = self.client.get(EXTENSIONS_URL)
        self.assertEqual(res.status_code, 200)

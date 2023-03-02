"""Tests of the extensions extension."""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.utils.tests import create_testuser

from .models import Extension

EXTENSIONS_URL = reverse("collectivo:collectivo.extensions:extension-list")


class ExtensionsTests(TestCase):
    """Test the extensions extension."""

    def setUp(self):
        """Prepare API client and a test extension."""
        self.client = APIClient()
        self.user = create_testuser(superuser=True)
        self.client.force_authenticate(self.user)
        self.name = "my_extension"
        self.setup_payload = {"name": self.name}
        res = self.client.post(EXTENSIONS_URL, self.setup_payload)
        self.detail_url = EXTENSIONS_URL + str(res.data["id"]) + "/"

    def test_create_extension(self):
        """Test extension is registered."""
        exists = Extension.objects.filter(name=self.name).exists()
        self.assertTrue(exists)

    def test_delete_extension(self):
        """Test removing extension."""
        self.client.delete(self.detail_url)
        exists = Extension.objects.filter(name=self.name).exists()
        self.assertFalse(exists)

    def test_change_extension(self):
        """Test that attributes except name can be changed."""
        payload = {"name": "new_name", "version": "777"}
        self.client.patch(self.detail_url, payload)
        ext = Extension.objects.get(name=self.name)
        self.assertEqual(ext.name, self.name)
        self.assertEqual(ext.version, payload["version"])

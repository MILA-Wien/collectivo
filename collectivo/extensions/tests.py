"""Tests of the extensions module."""
from django.urls import reverse
from django.test import TestCase

from collectivo.auth.clients import CollectivoAPIClient
from .models import Extension
from .utils import register_extension


EXTENSIONS_URL = reverse('collectivo:collectivo.extensions:extension-list')


class InternalApiTests(TestCase):
    """Test functions to use API internally."""

    def test_register_extension(self):
        """Test registering an extension through internal API."""
        # A first call should create new entry
        res = register_extension('my_extension', version='1.0.0')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data['version'], '1.0.0')

        # A second call should update existing entry
        res = register_extension('my_extension', version='1.0.1')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data['version'], '1.0.1')


class PublicExtensionsApiTests(TestCase):
    """Test the publicly available ingredients API."""

    def test_extension_API_fails(self):
        """Test extension API is not available for public user."""
        self.client = CollectivoAPIClient()
        self.name = 'my_extension'
        self.setup_payload = {'name': self.name}
        res = self.client.post(EXTENSIONS_URL, self.setup_payload)
        self.assertEquals(res.status_code, 403)


class PrivateExtensionsApiTests(TestCase):
    """Test the publicly available ingredients API."""

    def setUp(self):
        """Prepare API client and a test extension."""
        self.client = CollectivoAPIClient()
        self.client.force_roles(['superuser'])
        self.name = 'my_extension'
        self.setup_payload = {'name': self.name}
        self.client.post(EXTENSIONS_URL, self.setup_payload)
        self.detail_url = EXTENSIONS_URL + self.name + '/'

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
        payload = {'name': 'new_name', 'version': '777'}
        self.client.patch(self.detail_url, payload)
        ext = Extension.objects.get(name=self.name)
        self.assertEqual(ext.name, self.name)
        self.assertEqual(ext.version, payload['version'])

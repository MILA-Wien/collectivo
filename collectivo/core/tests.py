"""Tests for the core extension."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.extensions.models import Extension
from collectivo.menus.models import Menu
from collectivo.version import __version__

from .permissions import HasGroup, IsSuperuser


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
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username="testuser")
        self.client.force_authenticate(self.user)

    def test_get_version(self):
        """Test getting current version is correct."""
        res = self.client.get(reverse("collectivo:collectivo.core:version"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["version"], __version__)

    def test_is_superuser_permission(self):
        """Test that the superuser permission works correctly."""
        request = RequestFactory().get("/")
        request.user = self.user
        self.assertFalse(IsSuperuser().has_permission(request, None))
        group = Group.objects.get(name="collectivo.core.admin")
        self.user.groups.add(group)
        self.assertTrue(IsSuperuser().has_permission(request, None))

    def test_has_group_permission(self):
        """Test that the has group permission works correctly."""

        class SomeGroupView:
            """View that requires some group."""

            required_groups = ["some group"]

        request = RequestFactory().get("/")
        request.user = self.user
        view = SomeGroupView()
        self.assertFalse(HasGroup().has_permission(request, view))
        group = Group.objects.create(name="some group")
        self.user.groups.add(group)
        self.assertTrue(HasGroup().has_permission(request, view))

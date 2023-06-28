"""Tests for the core extension."""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.core.models import Permission, PermissionGroup
from collectivo.extensions.models import Extension
from collectivo.menus.models import Menu
from collectivo.utils.permissions import HasPerm, IsSuperuser
from collectivo.utils.test import create_testuser
from collectivo.version import __version__

PROFILES_URL = reverse("collectivo.core:users-extended-list")


class CoreSetupTests(TestCase):
    """Test extension is registered correctly."""

    def test_default_menus(self):
        """Test default menus exist."""
        for name in ["main", "admin"]:
            self.assertTrue(
                Menu.objects.filter(
                    extension=Extension.objects.get(name="core"), name=name
                ).exists()
            )


class UserApiTests(TestCase):
    """Test the user and group endpoints."""

    def setUp(self):
        """Set up the test client."""
        self.client = APIClient()
        self.user = create_testuser(superuser=True)
        self.client.force_authenticate(self.user)

    def test_user_endpoint(self):
        """Test the user endpoint."""
        res = self.client.get(reverse("collectivo.core:user-list"))
        self.assertEqual(res.status_code, 200)

    def test_users_extended_endpoint(self):
        """Test that an admin can get the extended profiles data."""
        res = self.client.get(PROFILES_URL)
        self.assertEqual(res.status_code, 200)


class CoreApiTests(TestCase):
    """Test the core API."""

    def setUp(self):
        """Set up the test client."""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username="testuser")
        self.client.force_authenticate(self.user)

    def test_get_api_docs(self):
        """Test getting the API docs."""
        if settings.COLLECTIVO["api_docs"]:
            res = self.client.get("/api/schema/?version=0.1.0")
            self.assertEqual(res.status_code, 200)

    def test_get_version(self):
        """Test getting current version is correct."""
        res = self.client.get(reverse("collectivo.core:version"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["version"], __version__)

    def test_update_username(self):
        """Test the username is updated when email is changed."""
        user = get_user_model().objects.create(email="123")
        self.assertEqual(user.username, "123")
        user.email = "456"
        user.save()
        self.assertEqual(user.username, "456")

    def test_capitalize_names(self):
        """Test the first letter of names is capitalized."""
        user = get_user_model().objects.create(
            first_name="test test", last_name="user user"
        )
        self.assertEqual(user.first_name, "Test test")
        self.assertEqual(user.last_name, "User user")

    def test_is_superuser_permission(self):
        """Test that the superuser permission works correctly."""
        request = RequestFactory().get("/")
        request.user = self.user
        self.assertFalse(IsSuperuser().has_permission(request, None))
        group = PermissionGroup.objects.get(
            name="superuser", extension=Extension.objects.get(name="core")
        )
        self.user.permission_groups.add(group)
        self.assertTrue(IsSuperuser().has_permission(request, None))

    def test_has_group_permission(self):
        """Test that the has group permission works correctly."""

        class SomeGroupView:
            """View that requires some group."""

            required_perms = {
                "ALL": [("some perm", None)],
            }

        request = RequestFactory().get("/")
        request.user = self.user
        view = SomeGroupView()
        self.assertFalse(HasPerm().has_permission(request, view))
        group = PermissionGroup.objects.create(name="some group")
        perm = Permission.objects.create(name="some perm")
        group.permissions.add(perm)
        group.save()
        self.user.permission_groups.add(group)
        self.assertTrue(HasPerm().has_permission(request, view))

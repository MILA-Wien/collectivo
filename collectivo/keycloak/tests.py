"""Tests for the keycloak extension."""
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from keycloak.exceptions import KeycloakDeleteError
from rest_framework.test import APIClient

from collectivo.version import __version__

from .authentication import KeycloakAuthentication
from .keycloak import KeycloakAPI

User = get_user_model()


class KeycloakTestCase(TestCase):
    """Test case for the keycloak extension."""

    def setUp(self):
        """Create a test user on keycloak."""
        self.keycloak = KeycloakAPI()
        self.tearDown()  # In case a previous test failed
        self.keycloak_user_id = self.keycloak.create_user(
            first_name="test",
            last_name="user",
            email="testuser@example.com",
            email_verified=True,
        )
        self.keycloak.set_user_password(
            self.keycloak_user_id, "Test123!", temporary=False
        )
        token = self.keycloak.openid.token("testuser@example.com", "Test123!")
        self.access_token = token["access_token"]

    def tearDown(self):
        """Delete the test user."""
        try:
            self.keycloak.delete_user_by_email("testuser@example.com")
        except KeycloakDeleteError:
            pass

    def test_keycloak_user_creation(self):
        """Test authenticated request creates keycloak user."""
        factory = RequestFactory()
        request = factory.get("", HTTP_AUTHORIZATION=self.access_token)
        for _ in range(2):
            user, auth = KeycloakAuthentication().authenticate(request)
            self.assertEqual(user.keycloak.uuid, self.keycloak_user_id)
            self.assertEqual(auth, self.access_token)

    def test_keycloak_authentication_succeeds(self):
        """Test that the keycloak authentication works with correct token."""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.access_token)
        res = client.get("/api/core/about/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["version"], __version__)

    def test_keycloak_authentication_fails(self):
        """Test that the keycloak authentication fails with bad token."""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bad token")
        res = client.get("/api/core/about/")
        self.assertEqual(res.status_code, 401)


class KeycloakSynchronizationTests(TestCase):
    """Test case for the keycloak extension."""

    def setUp(self):
        """Create a test user on collectivo."""
        self.keycloak = KeycloakAPI()
        self.user = User.objects.create(
            username="testuser@example.com",
            email="testuser@example.com",
            first_name="test",
            last_name="user",
        )

    def tearDown(self):
        """Delete the test user."""
        try:
            self.keycloak.delete_user_by_email("testuser@example.com")
        except KeycloakDeleteError:
            pass

    def test_creating_user_creates_keycloak_user(self):
        """Test that creating a user creates a keycloak user."""
        self.assertEqual(self.user.keycloak.user, self.user)

    def test_updating_user_updates_keycloak_user(self):
        """Test that updating a user updates a keycloak user."""
        self.user.first_name = "new name"
        self.user.save()
        user = self.keycloak.admin.get_user(self.user.keycloak.uuid)
        self.assertEqual(user["firstName"], "new name")

    # def test_deleting_user_deletes_keycloak_user(self):
    #     """Test that deleting a user deletes a keycloak user."""
    #     self.user.delete()
    #     with self.assertRaises(Exception):
    #         self.user.keycloak

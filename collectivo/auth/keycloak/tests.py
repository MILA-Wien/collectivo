"""Tests for the keycloak extension."""
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from keycloak.exceptions import KeycloakDeleteError, KeycloakGetError
from rest_framework.test import APIClient

from collectivo.version import __version__

from .api import KeycloakAPI
from .authentication import KeycloakAuthentication
from .models import KeycloakUser

User = get_user_model()

TEST_USER = {
    "username": "testuser@example.com",
    "email": "testuser@example.com",
    "first_name": "test",
    "last_name": "user",
}


def delete_keycloak_test_user():
    """Delete test user from keycloak."""
    keycloak = KeycloakAPI()
    try:
        keycloak.delete_user_by_email(TEST_USER["email"])
    except KeycloakDeleteError:
        pass


# TODO: Email verification test


class KeycloakAuthenticationTests(TestCase):
    """Test using keycloak for authentication."""

    def setUp(self):
        """Create a test user on keycloak."""
        delete_keycloak_test_user()  # In case a previous test failed
        self.keycloak = KeycloakAPI()
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
        delete_keycloak_test_user()

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

    def test_creating_user_with_existing_keycloak_account(self):
        """Test creating a user with an existing keycloak account.

        Since the email address already exists on keycloak, the user should
        automatically be linked to the existing keycloak account."""
        User.objects.create(**TEST_USER)
        user = User.objects.get(username=TEST_USER["username"])
        self.assertEqual(user.keycloak.uuid, self.keycloak_user_id)


class KeycloakSynchronizationTests(TestCase):
    """Test synchronizing user data with keycloak."""

    def setUp(self):
        """Create a test user on collectivo."""
        delete_keycloak_test_user()  # In case a previous test failed
        self.keycloak = KeycloakAPI()
        self.user = User.objects.create(**TEST_USER)

    def tearDown(self):
        """Delete the test user."""
        delete_keycloak_test_user()

    def test_creating_user_creates_keycloak_user(self):
        """Test that creating a user creates a keycloak user."""
        self.assertEqual(self.user.keycloak.user, self.user)

    def test_updating_user_updates_keycloak_user(self):
        """Test that updating a user updates a keycloak user."""
        self.user.first_name = "new name"
        self.user.save()
        user = self.keycloak.admin.get_user(self.user.keycloak.uuid)
        self.assertEqual(user["firstName"], "new name")

    def test_deleting_user_deletes_keycloak_user(self):
        """Test that deleting a user deletes a keycloak user."""
        self.user.delete()
        self.assertFalse(KeycloakUser.objects.filter(user=self.user).exists())
        with self.assertRaises(KeycloakGetError):
            self.keycloak.admin.get_user(self.user.keycloak.uuid)

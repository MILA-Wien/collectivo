"""Tests for the authentication client."""
from django.test import TestCase

from collectivo.users.models import AnonymousUser, User

from ..clients import AuthClient
from .fixtures import ADMIN_URL, EMAIL, PASSWORD, PRIVATE_URL, TEST_USER


class AuthClientTests(TestCase):
    """Tests for the authentication client."""

    def setUp(self):
        """Prepare client."""
        self.client: AuthClient = AuthClient()

    def test_force_authentication_succeeds(self):
        """Test force authentication with normal user succeeds."""
        self.client.force_authenticate(User())
        res = self.client.get(PRIVATE_URL)
        self.assertEqual(res.status_code, 200)

    def test_force_authentication_fails(self):
        """Test force authentication with anonymous user fails."""
        self.client.force_authenticate(AnonymousUser())
        res = self.client.get(PRIVATE_URL)
        self.assertEqual(res.status_code, 403)

    def test_as_user(self):
        """Test that with_roles can be used to test different roles."""
        client = AuthClient.as_user()
        res = client.get(PRIVATE_URL)
        self.assertEqual(res.status_code, 200)
        res = client.get(ADMIN_URL)
        self.assertEqual(res.status_code, 403)
        client = AuthClient.as_user(roles=["superuser"])
        res = client.get(ADMIN_URL)
        self.assertEqual(res.status_code, 200)

    def test_authorize_fails(self):
        """Test that autorization with email and password fails."""
        res = self.client.get(PRIVATE_URL)
        self.assertEqual(res.status_code, 403)

    def test_authorize_succeeds(self):
        """Test that autorization with email and password succeeds."""
        self.user = User.objects.create(**TEST_USER)
        self.user.set_password(PASSWORD, temporary=False)
        self.user.set_email_verified(True)
        self.client.authorize(EMAIL, PASSWORD)
        res = self.client.get(PRIVATE_URL)
        self.assertEqual(res.status_code, 200)

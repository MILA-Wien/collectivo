"""Test the keycloak authentication module."""
from django.test import RequestFactory, TestCase
from django.urls import reverse

from collectivo.users.models import Role, User
from collectivo.users.services import AuthService

from ..clients import AuthClient
from ..middleware import KeycloakMiddleware
from .fixtures import PASSWORD, TEST_USER


class KeycloakMiddlewareTests(TestCase):
    """Test the authentication of users through the keycloak middleware."""

    def setUp(self):
        """Prepare client and keycloak token."""
        self.auth_service = AuthService()
        self.client = AuthClient()
        self.user = User.objects.create(**TEST_USER)
        self.user.set_password(PASSWORD, temporary=False)
        self.user.set_email_verified(True)
        self.token = self.user.get_token(PASSWORD)
        self.access_token = self.token.access_token
        self.middleware = KeycloakMiddleware(None)
        self.factory = RequestFactory()

    def tearDown(self):
        """Delete test user."""
        self.auth_service.delete_user(self.user.user_id)

    def test_middleware_correct_token(self):
        """Test passing a correct token to the middleware."""
        request = self.factory.get("", HTTP_AUTHORIZATION=self.access_token)
        self.middleware.process_view(request, None, None, None)
        self.assertTrue(request.auth_user.is_authenticated)

    def test_middleware_empty_token(self):
        """Test passing a empty auth string to the middleware."""
        request = self.factory.get("", HTTP_AUTHORIZATION="")
        self.middleware.process_view(request, None, None, None)
        self.assertFalse(request.auth_user.is_authenticated)

    def test_middleware_bad_token_1(self):
        """Test passing an invalid token to the middleware."""
        request = self.factory.get("", HTTP_AUTHORIZATION="Token badtoken")
        self.middleware.process_view(request, None, None, None)
        self.assertFalse(request.auth_user.is_authenticated)

    def test_middleware_bad_token_2(self):
        """Test passing a faulty auth string to the middleware."""
        request = self.factory.get("", HTTP_AUTHORIZATION="bad bad bad")
        self.middleware.process_view(request, None, None, None)
        self.assertFalse(request.auth_user.is_authenticated)

    def test_middleware_bad_token_3(self):
        """Test passing a faulty auth string to the middleware."""
        request = self.factory.get("", HTTP_AUTHORIZATION="Token")
        self.middleware.process_view(request, None, None, None)
        self.assertFalse(request.auth_user.is_authenticated)


class AuthAPITests(TestCase):
    """Test the authentication of users through the keycloak middleware."""

    def setUp(self):
        """Prepare client and keycloak token."""
        self.auth_service = AuthService()
        self.client = AuthClient()
        self.user = User.objects.create(**TEST_USER)
        self.user.set_password(PASSWORD, temporary=False)
        self.user.set_email_verified(True)
        self.token = self.user.get_token(PASSWORD)
        self.access_token = self.token.access_token
        self.private_endpoint = "collectivo:collectivo.users:test_view_private"
        self.public_endpoint = "collectivo:collectivo.users:test_view_public"
        self.admin_endpoint = "collectivo:collectivo.users:test_view_admin"

    def tearDown(self):
        """Delete test user."""
        self.auth_service.delete_user(self.user.user_id)

    def test_private_api_with_correct_token(self):
        """Test that private api call with correct token succeeds."""
        self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
        res = self.client.get(reverse(self.private_endpoint))
        self.assertEqual(res.status_code, 200)

    def test_private_api_with_bad_token(self):
        """Test that private api call with bad token fails."""
        self.client.credentials(HTTP_AUTHORIZATION="Token " + "bad_token")
        res = self.client.get(reverse(self.private_endpoint))
        self.assertEqual(res.status_code, 401)

    def test_private_api_with_no_token(self):
        """Test that private api call with no token fails."""
        res = self.client.get(reverse(self.private_endpoint))
        self.assertEqual(res.status_code, 403)

    def test_public_api_with_correct_token(self):
        """Test that public api call with correct token succeeds."""
        self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
        res = self.client.get(reverse(self.public_endpoint))
        self.assertEqual(res.status_code, 200)

    def test_public_api_with_bad_token(self):
        """Test that public api call with bad token fails."""
        self.client.credentials(HTTP_AUTHORIZATION="Token " + "bad_token")
        res = self.client.get(reverse(self.public_endpoint))
        self.assertEqual(res.status_code, 401)

    def test_public_api_with_no_token(self):
        """Test that public api call with no token succeeds."""
        res = self.client.get(reverse(self.public_endpoint))
        self.assertEqual(res.status_code, 200)

    def test_admin_access_correct_token(self):
        """Test that admin api with admin token succeeds."""
        self.user.roles.add(Role.objects.get_or_create(name="superuser")[0])
        self.user.save()
        self.token = self.user.get_token(PASSWORD)
        self.access_token = self.token.access_token
        self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
        res = self.client.get(reverse(self.admin_endpoint))
        self.assertEqual(res.status_code, 200)

    def test_admin_access_bad_token(self):
        """Test that admin api with non-admin token fails."""
        self.client.credentials(HTTP_AUTHORIZATION=self.access_token)
        res = self.client.get(reverse(self.admin_endpoint))
        self.assertEqual(res.status_code, 403)

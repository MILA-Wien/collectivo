"""Testing clients of the authentication module."""
from rest_framework.test import APIClient, ForceAuthClientHandler

from collectivo.users.models import Role, SuperUser, User
from collectivo.users.services import AuthService
from collectivo.users.tests.fixtures import TEST_USER


class CustomForceAuthClientHandler(ForceAuthClientHandler):
    """Handler to force authentication with the user object."""

    def get_response(self, request):
        """Set forced user as user attribute."""
        request.auth_user = self._force_user if self._force_user else User()
        return super().get_response(request)


class AuthClient(APIClient):
    """APIClient with custom authorization methods."""

    def __init__(self, force=True, enforce_csrf_checks=False, **defaults):
        """Initialize client with custom handler."""
        super().__init__(enforce_csrf_checks, **defaults)

    def force_authenticate(self, user=None):
        """Force authentication with passed user."""
        self.handler = CustomForceAuthClientHandler()
        super().force_authenticate(user)

    @classmethod
    def as_superuser(cls):
        """Authorize as a generic superuser."""
        client = cls()
        client.force_authenticate(SuperUser())
        return client

    @classmethod
    def as_user(cls, roles: list[str] = []):
        """Authorize as a generic test user with given roles.

        This user is not synchronized with the auth service."""
        client = cls()
        user = User(**TEST_USER)
        user.user_id = "00000000-0000-0000-0000-000000000000"
        user.created = "2021-01-01"
        user.save_without_sync()
        for role in roles:
            role = Role.objects.get_or_create(name=role)[0]
            user.roles.add(role)
        client.force_authenticate(user)
        return client

    def authorize(self, email: str, password: str = "Test123!"):
        """Authorize test user with the auth service."""
        auth_service = AuthService()
        token = auth_service.openid.token(email, password)
        self.credentials(HTTP_AUTHORIZATION=token["access_token"])

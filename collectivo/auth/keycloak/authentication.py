"""Keycloak authentication middleware."""
from django.contrib.auth import get_user_model
from jwt import decode
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from .api import KeycloakAPI


class KeycloakAuthentication(authentication.BaseAuthentication):
    """Keycloak authentication middleware."""

    def __init__(self, *args, **kwargs):
        """One-time initialization of middleware."""
        super().__init__(*args, **kwargs)
        self.api = KeycloakAPI()

    def authenticate(self, request):
        """Authenticate a request or return exception."""
        try:
            return self.authenticate_with_keycloak(request)
        except Exception as e:
            raise AuthenticationFailed() from e

    def authenticate_with_keycloak(self, request):
        """Authenticate a request with keycloak."""
        if "HTTP_AUTHORIZATION" not in request.META:
            return None
        auth = request.META.get("HTTP_AUTHORIZATION").split()
        access_token = auth[1] if len(auth) == 2 else auth[0]
        self.api.openid.userinfo(access_token)
        data = decode(access_token, options={"verify_signature": False})
        User = get_user_model()
        try:
            user = User.objects.get(keycloak__uuid=data["sub"])
        except User.DoesNotExist:
            user = User.objects.create(
                username=data["email"],
                email=data["email"],
                first_name=data["given_name"],
                last_name=data["family_name"],
            )
            # KeycloakUser is created by a post-save signal in .models
            # User is loaded again to include the KeycloakUser
            user = User.objects.get(keycloak__uuid=data["sub"])
        return (user, access_token)

    def authenticate_header(self, request):
        """Return WWW-Authenticate header to be used in a 401 response."""
        return "Keycloak Access Token"

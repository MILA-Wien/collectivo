from django.conf import settings
from django.contrib.auth import get_user_model
from jwt import decode
from keycloak import KeycloakOpenID
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from .models import KeycloakUser


class KeycloakAuthentication(authentication.BaseAuthentication):
    def __init__(self, *args, **kwargs):
        """One-time initialization of middleware."""
        super().__init__(*args, **kwargs)
        config = settings.KEYCLOAK
        self.keycloak = KeycloakOpenID(
            server_url=config["SERVER_URL"],
            realm_name=config["REALM_NAME"],
            client_id=config["CLIENT_ID"],
            client_secret_key=config["CLIENT_SECRET_KEY"],
        )

    def authenticate(self, request):
        """Authenticate a request or return exception."""
        try:
            return self.authenticate_with_keycloak(request)
        except Exception as e:
            raise AuthenticationFailed() from e

    def authenticate_with_keycloak(self, request):
        """Authenticate a request with keycloak."""
        auth = request.META.get("HTTP_AUTHORIZATION").split()
        access_token = auth[1] if len(auth) == 2 else auth[0]
        self.keycloak.userinfo(access_token)
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
            # KeycloakUser is created by a signal
            # User is loaded again to include KeycloakUser
            user = User.objects.get(keycloak__uuid=data["sub"])
        return (user, access_token)

    def authenticate_header(self, request):
        """Return a string to be used as the value of the WWW-Authenticate
        header in a 401 response to the client."""
        return "Keycloak Access Token"

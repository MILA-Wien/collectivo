"""Keycloak authentication middleware."""
from django.contrib.auth import get_user_model
from jwt import decode
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from django.db import transaction
from django.db.utils import IntegrityError
from .api import KeycloakAPI
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


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
        except Exception:
            logger.exception("Authentication failed.")
            raise AuthenticationFailed()

    def authenticate_with_keycloak(self, request):
        """Authenticate a request with keycloak."""
        if "HTTP_AUTHORIZATION" not in request.META:
            return None
        auth = request.META.get("HTTP_AUTHORIZATION").split()
        access_token = auth[1] if len(auth) == 2 else auth[0]
        self.api.openid.userinfo(access_token)
        data = decode(access_token, options={"verify_signature": False})

        # Try to find User with given Keycloak UUID
        try:
            user = User.objects.get(keycloak__uuid=data["sub"])

        # If no User is found, try to find User with given email
        except User.DoesNotExist:
            try:
                with transaction.atomic():
                    # Keycloak connection is created by a post-save signal
                    # select_for_update locks row to prevent concurrent updates
                    user = User.objects.select_for_update().get(
                        email=data["email"]
                    )
                    user.save()

            # If no User is found, create a new User
            except User.DoesNotExist:
                try:
                    user = User.objects.create(
                        username=data["email"],
                        email=data["email"],
                        first_name=data["given_name"],
                        last_name=data["family_name"],
                    )

                # Pass if user was created in the meantime
                except IntegrityError:
                    pass

            # Reload user to include the post-save keycloak connection
            user = User.objects.get(keycloak__uuid=data["sub"])

        return (user, access_token)

    def authenticate_header(self, request):
        """Return WWW-Authenticate header to be used in a 401 response."""
        return "Keycloak Access Token"

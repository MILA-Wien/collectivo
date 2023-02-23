"""Middlewares of the authentication module."""
from django.conf import settings
from django.db import IntegrityError
from django.http.response import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from keycloak import KeycloakOpenID
from rest_framework.exceptions import AuthenticationFailed
from jwt import decode
import logging
from collectivo.errors import CollectivoError
from collectivo.users.models import User, AnonymousUser, Role

logger = logging.getLogger(__name__)


class KeycloakMiddleware(MiddlewareMixin):
    """KeyCloak Middleware for authentication and authorization."""

    def __init__(self, get_response):
        """One-time initialization of middleware."""
        self.get_response = get_response
        try:
            config = settings.KEYCLOAK
            self.keycloak = KeycloakOpenID(
                server_url=config["SERVER_URL"],
                realm_name=config["REALM_NAME"],
                client_id=config["CLIENT_ID"],
                client_secret_key=config["CLIENT_SECRET_KEY"],
            )
        except Exception as e:
            raise CollectivoError(
                f"Failed to set up keycloak connection: {repr(e)}"
            )

    def __call__(self, request):
        """Handle default requests."""
        return self.get_response(request)

    def auth_failed(self, request, log_message, error):
        """Return authentication failed message in log and API."""
        request_id = request.META.get("X-Correlation-ID", "NO-CORRELATION-ID")
        logger.debug(f"{request_id} {log_message}: {repr(error)}")
        return JsonResponse(
            {"detail": AuthenticationFailed.default_detail},
            status=AuthenticationFailed.status_code,
        )

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Check for authentication and try to get user from keycloak."""

        # Skip middleware if user is already provided
        if hasattr(request, "auth_user"):
            return None

        # Add anonymous user to request as default
        request.auth_user = AnonymousUser()

        # Return unauthenticated request if no authorization is found
        if "HTTP_AUTHORIZATION" not in request.META:
            return None

        # Retrieve token and user or return failure message
        try:
            auth = request.META.get("HTTP_AUTHORIZATION").split()
            access_token = auth[1] if len(auth) == 2 else auth[0]
        except Exception as e:
            return self.auth_failed(request, "Could not read token", e)

        # Check the validity of the token
        try:
            self.keycloak.userinfo(access_token)
        except Exception as e:
            return self.auth_failed(request, "Could not verify token", e)

        # Decode token
        try:
            data = decode(access_token, options={"verify_signature": False})
        except Exception as e:
            return self.auth_failed(request, "Could not decode token", e)

        # Get or create user from token data
        # User is authorized at this stage, so errors are only logged
        try:
            request.auth_user = User.objects.get(user_id=data.get("sub", None))
        except User.DoesNotExist:
            logger.debug(f"First-time user from keycloak: {data}")
            request.auth_user = User(user_id=data.get("sub", None))
        except Exception as e:
            return logger.debug(f"Could not retrieve user: {repr(e)}")

        try:
            request.auth_user.email = data.get("email")
            request.auth_user.first_name = data.get("given_name")
            request.auth_user.last_name = data.get("family_name")
            request.auth_user.save_without_sync()
            request.auth_user.roles.clear()
            for role in data.get("realm_access").get("roles"):
                request.auth_user.roles.add(
                    Role.objects.get_or_create(name=role)[0]
                )
            request.auth_user.save_without_sync()
        except IntegrityError:
            pass  # Can happen if user is already saved in another thread
        except Exception as e:
            return logger.debug(f"Could not create user: {repr(e)}")

        # Return authenticated request
        return None

"""Middlewares of the authentication module."""
from django.conf import settings
from django.http.response import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from keycloak import KeycloakOpenID
from rest_framework.exceptions import AuthenticationFailed
from jwt import decode
import logging
from .userinfo import UserInfo
from collectivo.errors import CollectivoError


logger = logging.getLogger(__name__)


class KeycloakMiddleware(MiddlewareMixin):
    """KeyCloak Middleware for authentication and authorization."""

    def __init__(self, get_response):
        """One-time initialization of middleware."""
        self.get_response = get_response  # Required by django
        try:
            self.setup_KeycloakOpenID()
        except Exception:
            raise CollectivoError(
                f"{__name__}: Failed to set up keycloak connection."
                "Please check settings.KEYCLOAK."
            )

    def setup_KeycloakOpenID(self):
        """Set up KeyCloakOpenID with given settings."""
        self.config = settings.KEYCLOAK  # TODO Use auth manager
        self.keycloak = KeycloakOpenID(
            server_url=self.config["SERVER_URL"],
            realm_name=self.config["REALM_NAME"],
            client_id=self.config["CLIENT_ID"],
            client_secret_key=self.config["CLIENT_SECRET_KEY"],
        )

    def __call__(self, request):
        """Handle default requests."""
        return self.get_response(request)  # Required by django

    def auth_failed(self, correlation_id, log_message, error):
        """Return authentication failed message in log and API."""
        logger.debug(f'{correlation_id} {log_message}: {repr(error)}')
        return JsonResponse(
            {"detail": AuthenticationFailed.default_detail},
            status=AuthenticationFailed.status_code,
        )

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Check for authentication and try to get user from keycloak."""
        # Skip middleware if userinfo is already provided
        if hasattr(request, 'userinfo'):
            return None

        # Add unauthenticated user to request
        request.userinfo = user = UserInfo()
        request_id = request.META.get(
            'X-Correlation-ID', 'NO-CORRELATION-ID')
        # Return unauthenticated request if no authorization is found
        if "HTTP_AUTHORIZATION" not in request.META:
            # logger.debug(f'No authorization found. Using public user.')
            return None

        # Retrieve token and user or return failure message
        try:
            auth = request.META.get("HTTP_AUTHORIZATION").split()
            access_token = auth[1] if len(auth) == 2 else auth[0]
        except Exception as e:
            return self.auth_failed(request_id, 'Could not read token', e)

        # Check the validity of the token
        try:
            self.keycloak.userinfo(access_token)
            user.is_authenticated = True
        except Exception as e:
            return self.auth_failed(request_id, 'Could not verify token', e)

        # Decode token
        try:
            data = decode(
                access_token, options={"verify_signature": False})
        except Exception as e:
            return self.auth_failed(request_id, 'Could not decode token', e)

        # Add userinfos to request
        try:
            user.user_id = data.get('sub', None)
            user.email = data.get('email', None)
            user.email_verified = data.get('email_verified', None)
            user.first_name = data.get('given_name', None)
            user.last_name = data.get('family_name', None)
            roles = data.get(
                'realm_access', {}).get('roles', [])
            for role in roles:
                user.roles.append(role)
        except Exception as e:
            return self.auth_failed(
                request_id, 'Could not extract userinfo', e)

        # Return authenticated request if no exception is thrown
        return None

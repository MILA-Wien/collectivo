"""Views of the authentication module."""

from rest_framework.views import APIView
from rest_framework.response import Response
from keycloak import KeycloakOpenID
from django.conf import settings
from .serializers import TokenSerializer
from .permissions import IsAuthenticated, IsSuperuser


# TODO Use auth manager
config = settings.KEYCLOAK
keycloak_manager = KeycloakOpenID(
    server_url=config["SERVER_URL"],
    client_id=config["REALM_NAME"],
    realm_name=config["CLIENT_ID"],
    client_secret_key=config["CLIENT_SECRET_KEY"],
)


class KeycloakTokenView(APIView):
    """API views of the keycloak token."""

    keycloak_manager = keycloak_manager

    def get_serializer(self, *args, **kwargs):
        """Return serializer for OpenAPI."""
        return TokenSerializer(*args, **kwargs)

    def post(self, request):
        """Return access/bearer token for given credentials."""
        # Validate input
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get token
        username = request.data['username']
        password = request.data['password']
        token = self.keycloak_manager.token(username, password)

        # TODO: Error for wrong password
        data = {
            'access_token': token['access_token'],
        }
        return Response(data)


class IsAuthenticatedView(APIView):
    """Test authentication."""

    def get(self, request):
        """Check authentication."""
        data = {
            'is_authenticated': request.is_authenticated,
        }
        return Response(data)


class PublicTestView(APIView):
    """API view that needs no authentication."""

    def get(self, request):
        """Return empty response."""
        return Response()


class PrivateTestView(APIView):
    """API view that needs authentication."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return empty response."""
        return Response()


class AdminTestView(APIView):
    """API view that needs authentication."""

    permission_classes = [IsSuperuser]

    def get(self, request):
        """Return empty response."""
        return Response()

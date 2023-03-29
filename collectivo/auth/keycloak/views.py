"""Views of the keycloak auth extension."""

from rest_framework.response import Response
from rest_framework.views import APIView

from .api import KeycloakAPI
from .serializers import TokenSerializer


class KeycloakTokenView(APIView):
    """View to receive keycloak token for development."""

    def get_serializer(self, *args, **kwargs):
        """Return serializer for OpenAPI."""
        return TokenSerializer(*args, **kwargs)

    def post(self, request):
        """Return access/bearer token for given credentials."""
        keycloak_manager = KeycloakAPI().openid

        # Validate input
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get token
        username = request.data["username"]
        password = request.data["password"]
        token = keycloak_manager.token(username, password)
        data = {"access_token": token["access_token"]}
        return Response(data)

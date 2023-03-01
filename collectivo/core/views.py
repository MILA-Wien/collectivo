"""Views of the core extension."""

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from collectivo.users.permissions import IsAuthenticated
from collectivo.version import __version__


class AboutView(APIView):
    """API view for information about the collectivo instance."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: OpenApiResponse()})
    def get(self, request):
        """Return information about the collectivo instance."""
        data = {
            "version": __version__,
        }
        return Response(data)

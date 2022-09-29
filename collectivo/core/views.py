"""Views of the core module."""
from rest_framework.views import APIView
from rest_framework.response import Response

from core.version import __version__


class GetVersion(APIView):
    """Get the current version of the project."""

    def get(self, request):
        """Return the current version of the project."""
        data = {
            'version': __version__,
        }
        return Response(data)

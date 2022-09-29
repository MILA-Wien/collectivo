"""Views of the extensions module."""
from rest_framework.views import APIView
from rest_framework.response import Response

from extensions.extension_manager import extension_manager


class GetExtensions(APIView):
    """API View for installed extensions."""

    def get(self, request):
        """Return installed extensions."""
        data = {
            'extensions': list(extension_manager.extensions.keys())
        }
        return Response(data)

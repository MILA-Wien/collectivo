"""Views of the extensions module."""
from rest_framework import viewsets

from collectivo.core.permissions import IsSuperuser

from .models import Extension
from .serializers import ExtensionCreateSerializer, ExtensionSerializer


class ExtensionViewSet(viewsets.ModelViewSet):
    """Manage extensions."""

    queryset = Extension.objects.all()
    permission_classes = [IsSuperuser]

    def get_serializer_class(self):
        """Set name to read-only except for create."""
        if self.request.method == "POST":
            return ExtensionCreateSerializer
        return ExtensionSerializer

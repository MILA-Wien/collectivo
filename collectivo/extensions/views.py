"""Views of the extensions module."""
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from collectivo.core.permissions import IsSuperuser
from collectivo.utils.mixins import SchemaMixin

from .models import Extension
from .serializers import ExtensionSerializer


class ExtensionViewSet(SchemaMixin, ListModelMixin, GenericViewSet):
    """Manage extensions."""

    queryset = Extension.objects.all()
    serializer_class = ExtensionSerializer
    permission_classes = [IsSuperuser]

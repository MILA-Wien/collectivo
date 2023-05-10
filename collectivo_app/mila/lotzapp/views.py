"""Views of the memberships extension."""
import logging

from django.contrib.auth import get_user_model
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from collectivo.utils.mixins import HistoryMixin, SchemaMixin
from collectivo.utils.permissions import IsSuperuser

from . import serializers
from .models import LotzappSettings, LotzappSync

User = get_user_model()
logger = logging.getLogger(__name__)


class LotzappSettingsViewSet(
    SchemaMixin, GenericViewSet, RetrieveModelMixin, UpdateModelMixin
):
    """ViewSet to manage lotzapp settings."""

    queryset = LotzappSettings.objects.all()
    serializer_class = serializers.LotzappSettingsSerializer
    permission_classes = [IsSuperuser]

    def get_object(self):
        """Return single entrys."""
        return self.queryset.get(pk=1)


class LotzappSyncViewSet(
    SchemaMixin,
    HistoryMixin,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """ViewSet to manage lotzapp sync actions."""

    queryset = LotzappSync.objects.all().order_by("-date")
    serializer_class = serializers.LotzappSyncSerializer
    permission_classes = [IsSuperuser]

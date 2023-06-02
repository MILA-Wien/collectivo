"""Viewsets of collectivo."""
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from collectivo.utils.mixins import (
    HistoryMixin,
    RetrieveModelByExtAndNameMixin,
    SchemaMixin,
)


class CollectivoViewSet(HistoryMixin, SchemaMixin, GenericViewSet):
    """GenericViewSet with History and Schema mixins."""

    pass


class CollectivoModelViewSet(HistoryMixin, SchemaMixin, ModelViewSet):
    """ModelViewSet with History and Schema mixins."""

    pass


class ExtensionModelViewSet(
    GenericViewSet,
    SchemaMixin,
    HistoryMixin,
    CreateModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    RetrieveModelByExtAndNameMixin,
):
    """ModelViewSet for models with a name and extension field."""

    pass


class SingleModelViewSet(
    HistoryMixin,
    SchemaMixin,
    GenericViewSet,
    RetrieveModelMixin,
    UpdateModelMixin,
):
    """ModelViewSet for SingleInstance models."""

    def get_object(self):
        """Return single entry."""
        return self.queryset.get(pk=1)

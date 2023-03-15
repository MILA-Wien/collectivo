"""History mixin for collectivo viewsets."""
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from collectivo.core.permissions import IsSuperuser


class HistoryMixin:
    """
    Adds an action 'history' to a viewset.

    The action returns the history of the model instance.
    The serializer needs a Meta attribute history with a history serializer.
    """

    @extend_schema(responses={200: OpenApiResponse()})
    @action(
        url_path="history",
        url_name="history",
        detail=True,
        permission_classes=[IsSuperuser],
    )
    def _history(self, request, pk):
        """Return model history."""
        obj = self.get_object()
        history = obj.history.all()
        serializer = self.get_serializer().Meta.history(history, many=True)
        return Response(serializer.data)

"""Mixin classes for collectivo viewsets."""
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from collectivo.utils.permissions import IsAuthenticated, IsSuperuser

from .schema import get_model_schema


class SelfMixin:
    """Filter queryset with the requests' user."""

    def get_object(self):
        """Return queryset entry with the request's user."""
        try:
            return self.queryset.get(user=self.request.user)
        except self.queryset.model.DoesNotExist:
            raise ParseError(f"{self.queryset.model} does not exist for user.")


class SchemaMixin:
    """Adds an action 'schema' to a viewset."""

    @extend_schema(responses={200: OpenApiResponse()})
    @action(
        detail=False,
        url_path="schema",
        url_name="schema",
        permission_classes=[IsAuthenticated],
    )
    def _schema(self, request):
        return get_model_schema(self)


class HistoryMixin:
    """Adds an action 'history' to a viewset."""

    @extend_schema(responses={200: OpenApiResponse()})
    @action(
        url_path="history",
        url_name="history",
        detail=True,
        permission_classes=[IsSuperuser],
    )
    def _history(self, request, pk):
        """Return model history."""

        class HistorySerializer(serializers.ModelSerializer):
            """Serializer to manage the history of a model."""

            class Meta:
                """Serializer settings."""

                model = self.get_serializer().Meta.model.history.model
                fields = "__all__"

        obj = self.get_object()
        history = obj.history.all()
        serializer = HistorySerializer(history, many=True)
        return Response(serializer.data)

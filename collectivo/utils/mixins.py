"""Mixin classes for collectivo viewsets."""

from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.request import Request
from rest_framework.response import Response

from collectivo.utils.permissions import IsAuthenticated, IsSuperuser

from .schema import get_model_schema


class RetrieveModelByExtAndNameMixin:
    """Mixin that requires extension and name to identify an object."""

    @action(
        methods=["GET"],
        detail=False,
        url_path=r"(?P<extension>\w+)/(?P<name>\w+)",
        url_name="detail",
    )
    def retrieve_with_params(self, request: Request, extension, name):
        """Get object based on extension and object name."""
        queryset = self.get_queryset()
        object = queryset.get(extension__name=extension, name=name)
        serializer = self.get_serializer(object)
        return Response(serializer.data)


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
    """Adds an action 'revert' to a viewset of a history model."""

    @extend_schema(responses={200: OpenApiResponse()})
    @action(
        url_path="revert",
        url_name="revert",
        detail=True,
        methods=["POST"],
        permission_classes=[IsSuperuser],
    )
    def _revert(self, request, pk):
        """Revert model to the state of the given history model."""
        history_object = self.get_object()
        history_object.instance.save()
        return Response("Success")


class BulkEditMixin:
    """Adds an action 'bulk_update' to a viewset."""

    @action(
        detail=False,
        methods=["put", "patch"],
        url_name="bulk_update",
        url_path="bulk_update",
    )
    def bulk_update(self, request, **kwargs):
        """Update multiple objects with a single request."""
        if not isinstance(request.data, list):
            raise ParseError("Invalid data (expected a list)")

        with transaction.atomic():
            for data in request.data:
                if not isinstance(data, dict) or "id" not in data:
                    raise ParseError("Invalid data (expected object with id)")
                instance = self.queryset.get(pk=data["id"])
                serializer = self.get_serializer(instance, data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        return Response()

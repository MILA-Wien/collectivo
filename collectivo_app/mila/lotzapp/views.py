"""Views of the memberships extension."""
from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from collectivo.utils.permissions import IsSuperuser
from collectivo.payments.models import Invoice
from collectivo.utils.mixins import SchemaMixin
from .models import LotzappAddress, LotzappInvoice, LotzappSettings
from . import serializers

User = get_user_model()


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


class LotzappInvoiceViewSet(GenericViewSet):
    """ViewSet to manage lotzapp invoice connection."""

    permission_classes = [IsSuperuser]

    @extend_schema(responses={200: OpenApiResponse()})
    @action(
        url_path="sync",
        url_name="sync",
        methods=["post"],
        detail=False,
    )
    def sync(self, request, *args, **kwargs):
        """Synchronize lotzapp with collectivo."""
        for invoice in Invoice.objects.all():
            LotzappInvoice.objects.get_or_create(invoice=invoice)[0].sync()
        return Response({"message": "Lotzapp has been synchronized."})


class LotzappAddressViewSet(GenericViewSet):
    """ViewSet to manage lotzapp address connection."""

    permission_classes = [IsSuperuser]

    @extend_schema(responses={200: OpenApiResponse()})
    @action(
        url_path="sync",
        url_name="sync",
        methods=["post"],
        detail=False,
    )
    def sync(self, request, *args, **kwargs):
        """Synchronize lotzapp with collectivo."""
        for user in User.objects.all():
            LotzappAddress.objects.get_or_create(user=user)[0].sync()
        return Response({"message": "Lotzapp has been synchronized."})

"""Views of the emails module."""
from rest_framework import viewsets

from collectivo.core.permissions import IsSuperuser
from collectivo.filters import get_filterset
from collectivo.utils.schema import SchemaMixin

from . import models, serializers


class EmailDesignViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage email designs."""

    permission_classes = [IsSuperuser]
    serializer_class = serializers.EmailDesignSerializer
    # filterset_fields = get_filterset(serializers.EmailDesignSerializer)
    queryset = models.EmailDesign.objects.all()


class EmailTemplateViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage email templates."""

    permission_classes = [IsSuperuser]
    serializer_class = serializers.EmailTemplateSerializer
    # filterset_fields = get_filterset(serializers.EmailTemplateSerializer)
    queryset = models.EmailTemplate.objects.all()


class EmailCampaignViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage email campaigns (mass email orders)."""

    permission_classes = [IsSuperuser]
    serializer_class = serializers.EmailCampaignSerializer
    # filterset_fields = get_filterset(serializers.EmailCampaignSerializer)
    queryset = models.EmailCampaign.objects.all()

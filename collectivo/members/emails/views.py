"""Views of the emails module."""
from rest_framework import viewsets

from collectivo.filters import get_filterset_fields
from collectivo.members.permissions import IsMembersAdmin
from collectivo.views import SchemaMixin

from . import models, serializers


class EmailDesignViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage email designs."""

    permission_classes = [IsMembersAdmin]
    serializer_class = serializers.EmailDesignSerializer
    filterset_fields = get_filterset_fields(serializers.EmailDesignSerializer)
    queryset = models.EmailDesign.objects.all()


class EmailTemplateViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage email templates."""

    permission_classes = [IsMembersAdmin]
    serializer_class = serializers.EmailTemplateSerializer
    filterset_fields = get_filterset_fields(
        serializers.EmailTemplateSerializer
    )
    queryset = models.EmailTemplate.objects.all()


class EmailCampaignViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage email campaigns (mass email orders)."""

    permission_classes = [IsMembersAdmin]
    serializer_class = serializers.EmailCampaignSerializer
    filterset_fields = get_filterset_fields(
        serializers.EmailCampaignSerializer
    )
    queryset = models.EmailCampaign.objects.all()


class EmailAutomationViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage email automations."""

    permission_classes = [IsMembersAdmin]
    serializer_class = serializers.EmailAutomationSerializer
    filterset_fields = get_filterset_fields(
        serializers.EmailAutomationSerializer
    )
    queryset = models.EmailAutomation.objects.all()

"""Views of the payments extension."""
from rest_framework import viewsets

from collectivo.utils.mixins import SchemaMixin
from collectivo.utils.permissions import HasGroup

from . import models, serializers


class PaymentProfileViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage payment users."""

    permission_classes = [HasGroup]
    required_groups = ["collectivo.payments.admin"]
    serializer_class = serializers.PaymentProfileSerializer
    queryset = models.Payment.objects.all()


class PaymentViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage payments."""

    permission_classes = [HasGroup]
    required_groups = ["collectivo.payments.admin"]
    serializer_class = serializers.PaymentSerializer
    queryset = models.Payment.objects.all()


class SubscriptionViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage subscriptions."""

    permission_classes = [HasGroup]
    required_groups = ["collectivo.payments.admin"]
    serializer_class = serializers.SubscriptionSerializer
    queryset = models.Payment.objects.all()

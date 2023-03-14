"""Views of the emails module."""
from rest_framework import viewsets

from collectivo.payments.permissions import IsPaymentsAdmin
from collectivo.utils.schema import SchemaMixin

from . import models, serializers


class PaymentProfileViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage payment users."""

    permission_classes = [IsPaymentsAdmin]
    serializer_class = serializers.PaymentProfileSerializer
    queryset = models.Payment.objects.all()


class PaymentViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage payments."""

    permission_classes = [IsPaymentsAdmin]
    serializer_class = serializers.PaymentSerializer
    queryset = models.Payment.objects.all()


class SubscriptionViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage subscriptions."""

    permission_classes = [IsPaymentsAdmin]
    serializer_class = serializers.SubscriptionSerializer
    queryset = models.Payment.objects.all()

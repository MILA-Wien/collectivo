"""Views of the payments extension."""
from rest_framework import mixins, viewsets

from collectivo.utils.filters import get_filterset, get_ordering_fields
from collectivo.utils.mixins import HistoryMixin, SchemaMixin, SelfMixin
from collectivo.utils.permissions import HasPerm, IsAuthenticated

from . import models, serializers


class ProfileViewSet(SchemaMixin, viewsets.ModelViewSet):
    """ViewSet for admins to manage payment profiles."""

    queryset = models.PaymentProfile.objects.all()
    serializer_class = serializers.PaymentProfileSerializer
    permission_classes = [HasPerm]
    required_perms = {
        "GET": [("view_profiles", "payments")],
        "ALL": [("edit_profiles", "payments")],
    }
    filterset_class = get_filterset(serializer_class)
    ordering_fields = get_ordering_fields(serializer_class)


class ProfileSelfViewSet(
    SelfMixin,
    SchemaMixin,
    HistoryMixin,
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    """ViewSet for users to manage their own payment profile."""

    queryset = models.PaymentProfile.objects.all()
    serializer_class = serializers.PaymentProfileSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = get_filterset(serializer_class)
    ordering_fields = get_ordering_fields(serializer_class)


class InvoiceViewSet(HistoryMixin, SchemaMixin, viewsets.ModelViewSet):
    """ViewSet for admins to manage subscriptions."""

    permission_classes = [HasPerm]
    required_perms = {
        "GET": [("view_payments", "payments")],
        "ALL": [("edit_payments", "payments")],
    }
    serializer_class = serializers.InvoiceSerializer
    queryset = models.Invoice.objects.all()
    filterset_class = get_filterset(serializer_class)
    ordering_fields = get_ordering_fields(serializer_class)


class SubscriptionViewSet(HistoryMixin, SchemaMixin, viewsets.ModelViewSet):
    """ViewSet for admins to manage subscriptions."""

    permission_classes = [HasPerm]
    required_perms = {
        "GET": [("view_payments", "payments")],
        "ALL": [("edit_payments", "payments")],
    }
    serializer_class = serializers.SubscriptionSerializer
    queryset = models.Subscription.objects.all()
    filterset_class = get_filterset(serializer_class)
    ordering_fields = get_ordering_fields(serializer_class)

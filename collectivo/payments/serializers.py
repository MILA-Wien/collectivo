"""Serializers of the payments module."""
from rest_framework import serializers

from . import models


class PaymentProfileSerializer(serializers.ModelSerializer):
    """Serializer for payment profiles."""

    class Meta:
        """Serializer settings."""

        model = models.Payment
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments."""

    class Meta:
        """Serializer settings."""

        model = models.Payment
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscriptions."""

    class Meta:
        """Serializer settings."""

        model = models.Subscription
        fields = "__all__"

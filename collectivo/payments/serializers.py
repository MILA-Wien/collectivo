"""Serializers of the payments extension."""
from rest_framework import serializers

from collectivo.utils.schema import Schema
from collectivo.utils.serializers import UserIsPk

from . import models


class PaymentProfileSerializer(UserIsPk):
    """Serializer for payment profiles."""

    class Meta:
        """Serializer settings."""

        label = "Payment data"
        model = models.PaymentProfile
        fields = "__all__"
        read_only_fields = ["user"]
        schema: Schema = {
            "actions": ["retrieve", "update"],
            "fields": {
                "user": {"visible": False},
                "bank_account_iban": {
                    "label": "IBAN",
                    "validators": ["iban"],
                    "required": True,
                },
                "bank_account_owner": {"required": True},
            },
        }


class ItemEntrySerializer(serializers.ModelSerializer):
    """Serializer for items."""

    class Meta:
        """Serializer settings."""

        model = models.ItemEntry
        fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for invoices."""

    items = serializers.PrimaryKeyRelatedField(
        queryset=models.ItemEntry.objects.all(), many=True
    )
    amount = serializers.SerializerMethodField()

    def get_amount(self, obj):
        """Get the total amount of the invoice."""
        return sum([item.amount * item.price for item in obj.items.all()])

    class Meta:
        """Serializer settings."""

        model = models.Invoice
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscriptions."""

    items = serializers.PrimaryKeyRelatedField(
        queryset=models.ItemEntry.objects.all(), many=True
    )
    invoices = serializers.PrimaryKeyRelatedField(
        queryset=models.Invoice.objects.all(), many=True
    )
    amount = serializers.SerializerMethodField()

    def get_amount(self, obj):
        """Get the total amount of the invoice."""
        return sum([item.amount * item.price for item in obj.items.all()])

    class Meta:
        """Serializer settings."""

        model = models.Subscription
        fields = "__all__"

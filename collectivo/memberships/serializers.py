"""Serializers of the memberships extension."""
from django.db.models import Avg, Max, Sum
from rest_framework import serializers
from collectivo.extensions.models import Extension
from django.contrib.auth import get_user_model
from collectivo.utils.serializers import UserFields

from . import models

User = get_user_model()


class MembershipSerializer(UserFields):
    """Serializer for memberships."""

    shares_paid = serializers.SerializerMethodField()
    user__tags = serializers.PrimaryKeyRelatedField(
        many=True,
        source="user.tags",
        read_only=True,
        label="Memberships",
    )

    class Meta:
        """Serializer settings."""

        model = models.Membership
        fields = "__all__"
        read_only_fields = ["id", "number"]

    def get_shares_paid(self, obj):
        """Get shares paid for this membership."""
        if not obj.type.has_shares:
            return 0
        try:
            from collectivo.payments.models import (
                ItemEntry,
                ItemType,
                ItemTypeCategory,
            )
        except ImportError:
            return 0

        extension = Extension.objects.get(name="memberships")
        item_category = ItemTypeCategory.objects.get_or_create(
            name="Shares", extension=extension
        )[0]
        item_type = ItemType.objects.get_or_create(
            name=obj.type.name,
            category=item_category,
            extension=extension,
        )[0]
        entries = ItemEntry.objects.filter(
            type=item_type,
            invoice__payment_from=obj.user.account,
            invoice__status="paid",
        )
        return (
            sum([entry.amount * entry.price for entry in entries])
            / obj.type.shares_amount_per_share
        )


class MembershipSelfSerializer(serializers.ModelSerializer):
    """Serializer for memberships."""

    class Meta:
        """Serializer settings."""

        model = models.Membership
        fields = "__all__"
        depth = 1

    def get_fields(self):
        """Set all fields to read only except shares_signed."""
        fields = super().get_fields()
        for field_name, field in fields.items():
            if field_name != "shares_signed":
                field.read_only = True
        return fields

    def validate(self, data):
        """Validate the data."""
        if data.get("shares_signed", None) is not None:
            if data["shares_signed"] < self.instance.shares_signed:
                raise serializers.ValidationError(
                    "You cannot lower the number of shares you signed."
                )
        return data


class MembershipProfileSerializer(serializers.ModelSerializer):
    """Serializer for tag profiles."""

    memberships = serializers.PrimaryKeyRelatedField(
        many=True, queryset=models.Membership.objects.all()
    )

    class Meta:
        """Serializer settings."""

        model = User
        fields = ["id", "memberships"]
        read_only_fields = ["id", "memberships"]


class MembershipTypeSerializer(serializers.ModelSerializer):
    """Serializer for membership types."""

    statistics = serializers.SerializerMethodField()

    class Meta:
        """Serializer settings."""

        model = models.MembershipType
        fields = "__all__"
        read_only_fields = ["id"]

    def get_statistics(self, obj):
        """Get statistics for this membership type."""
        try:
            statistics = {
                "memberships": obj.memberships.count(),
                **{
                    f"with status: {status.name}": obj.memberships.filter(
                        status=status
                    ).count()
                    for status in obj.statuses.all()
                },
                **obj.memberships.aggregate(Sum("shares_signed")),
                **obj.memberships.aggregate(Avg("shares_signed")),
                **obj.memberships.aggregate(Max("shares_signed")),
            }
        except Exception as e:
            statistics = {"error trying to calculate statistics": str(e)}
        return statistics


class MembershipStatusSerializer(serializers.ModelSerializer):
    """Serializer for membership statuses."""

    class Meta:
        """Serializer settings."""

        model = models.MembershipStatus
        fields = "__all__"
        read_only_fields = ["id"]

"""Serializers of the memberships extension."""
from django.db.models import Avg, Max, Sum
from rest_framework import serializers
from django.contrib.auth import get_user_model
from collectivo.utils.serializers import UserFields

from . import models

User = get_user_model()


class MembershipSerializer(UserFields):
    """Serializer for memberships."""

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


class MembershipSelfSerializer(serializers.ModelSerializer):
    """Serializer for memberships."""

    class Meta:
        """Serializer settings."""

        model = models.Membership
        fields = "__all__"
        read_only_fields = ["id", "number"]
        depth = 1


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

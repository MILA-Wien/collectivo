"""Serializers of the memberships extension."""
from rest_framework import serializers

from . import models


class MembershipSerializer(serializers.ModelSerializer):
    """Serializer for memberships."""

    class Meta:
        """Serializer settings."""

        model = models.Membership
        exclude = ["id"]
        read_only_fields = ["number"]


class MembershipTypeSerializer(serializers.ModelSerializer):
    """Serializer for membership types."""

    class Meta:
        """Serializer settings."""

        model = models.MembershipType
        exclude = ["id"]


class MembershipStatusSerializer(serializers.ModelSerializer):
    """Serializer for membership statuses."""

    class Meta:
        """Serializer settings."""

        model = models.MembershipStatus
        exclude = ["id"]

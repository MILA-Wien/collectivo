"""Serializers of the collectivo user experience module."""
from rest_framework import serializers

from .models import Assignment, Shift, ShiftUser


class ShiftSerializer(serializers.ModelSerializer):
    """Serializer for shift."""

    class Meta:
        """Serializer settings."""

        model = Shift
        fields = "__all__"

    def create(self, validated_data):
        """Create a new shift."""
        shift = Shift.objects.create(**validated_data)
        required_users = validated_data.get("required_users")
        for i in range(required_users):
            Assignment.objects.create(shift=shift)

        return shift


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for individual shift."""

    class Meta:
        """Serializer settings."""

        model = Assignment
        fields = "__all__"


class ShiftUserSerializer(serializers.ModelSerializer):
    """Serializer for shift user."""

    class Meta:
        """Serializer settings."""

        model = ShiftUser
        fields = "__all__"

"""Serializers of the collectivo user experience module."""
from rest_framework import serializers

from .models import GeneralShift, IndividualShift, ShiftUser


class IndividualShiftSerializer(serializers.ModelSerializer):
    """Serializer for individual shift."""

    class Meta:
        """Serializer settings."""

        model = IndividualShift
        fields = "__all__"


class GeneralShiftSerializer(serializers.ModelSerializer):
    """Serializer for general shift."""

    individual_shifts = IndividualShiftSerializer(many=True)

    class Meta:
        """Serializer settings."""

        model = GeneralShift
        fields = "__all__"

    def create(self, validated_data):
        """Create a new general shift."""
        individual_shifts_data = validated_data.pop("individual_shifts")
        general_shift = GeneralShift.objects.create(**validated_data)
        required_users = validated_data.get("required_users")
        for i in range(required_users):
            IndividualShift.objects.create(**individual_shifts_data[i])
        return general_shift


class ShiftUserSerializer(serializers.ModelSerializer):
    """Serializer for shift user."""

    class Meta:
        """Serializer settings."""

        model = ShiftUser
        fields = "__all__"

"""Serializers of the collectivo user experience module."""
from rest_framework import serializers

from .models import GeneralShift, IndividualShift, ShiftUser


class GeneralShiftSerializer(serializers.ModelSerializer):
    """Serializer for general shift."""

    # individual_shifts = IndividualShiftSerializer(many=True)

    class Meta:
        """Serializer settings."""

        model = GeneralShift
        fields = "__all__"

    def create(self, validated_data):
        """Create a new general shift."""
        general_shift = GeneralShift.objects.create(**validated_data)
        required_users = validated_data.get("required_users")
        for i in range(required_users):
            IndividualShift.objects.create(general_shift=general_shift)

        return general_shift


class IndividualShiftSerializer(serializers.ModelSerializer):
    """Serializer for individual shift."""

    class Meta:
        """Serializer settings."""

        model = IndividualShift
        fields = "__all__"

    def assign_user_to_shift(self, user, individual_shift):
        """Assign user to individual shift."""
        individual_shift.user = user
        individual_shift.save()


class ShiftUserSerializer(serializers.ModelSerializer):
    """Serializer for shift user."""

    class Meta:
        """Serializer settings."""

        model = ShiftUser
        fields = "__all__"
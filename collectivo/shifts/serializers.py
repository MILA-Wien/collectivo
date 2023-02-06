"""Serializers of the collectivo user experience module."""
from rest_framework import serializers

from .models import GeneralShift, IndividualShift, ShiftUser


class GeneralShiftSerializer(serializers.ModelSerializer):
    """Serializer for general shift."""

    class Meta:
        """Serializer settings."""

        model = GeneralShift
        fields = "__all__"


class IndividualShiftSerializer(serializers.ModelSerializer):
    """Serializer for individual shift."""

    class Meta:
        """Serializer settings."""

        model = IndividualShift
        fields = "__all__"


class ShiftUserSerializer(serializers.ModelSerializer):
    """Serializer for shift user."""

    class Meta:
        """Serializer settings."""

        model = ShiftUser
        fields = "__all__"

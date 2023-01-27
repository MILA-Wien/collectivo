"""Serializers of the collectivo user experience module."""
from rest_framework import serializers

from .models import GeneralShift


class ShiftSerializer(serializers.ModelSerializer):
    """Serializer for existing menu objects."""

    class Meta:
        """
        Serializer settings.
        """

        model = GeneralShift
        fields = "__all__"

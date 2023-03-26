"""Serializers of the extensions module."""
from rest_framework import serializers

from .models import Extension


class ExtensionSerializer(serializers.ModelSerializer):
    """Serializer for extension objects."""

    class Meta:
        """Serializer settings."""

        model = Extension
        fields = "__all__"

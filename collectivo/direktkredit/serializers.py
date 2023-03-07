"""Serializers of the extension."""
from rest_framework import serializers
from .models import DirektkreditModel


class DirektkreditSerializer(serializers.ModelSerializer):
    """Serializer for Direktkredit model."""

    class Meta:
        """Serializer settings."""

        model = DirektkreditModel
        fields = '__all__'

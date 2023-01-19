"""Serializers of the extensions module."""
from rest_framework import serializers
from .models import Extension


class ExtensionCreateSerializer(serializers.ModelSerializer):
    """Serializer to create new extension objects."""

    class Meta:
        """Serializer settings."""

        model = Extension
        fields = '__all__'


class ExtensionSerializer(serializers.ModelSerializer):
    """Serializer for existing extension objects."""

    class Meta:
        """
        Serializer settings.

        The name cannot be changed because it is the primary key to identify
        the extension. A new extension has to be created to set a new name.
        """

        model = Extension
        fields = '__all__'
        read_only_fields = ('name', )

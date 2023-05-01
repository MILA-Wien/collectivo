"""Serializers of the profiles extension."""

from rest_framework import serializers

from . import models


class LotzappSettingsSerializer(serializers.ModelSerializer):
    """Serializer for members to manage their own data."""

    class Meta:
        """Serializer settings."""

        model = models.LotzappSettings
        fields = "__all__"
        extra_kwargs = {"lotzapp_pass": {"write_only": True}}

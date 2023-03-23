"""Serializers of the tags extension."""
from rest_framework import serializers

from . import models


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        """Serializer settings."""

        model = models.Tag
        fields = "__all__"
        read_only_fields = ("id", "extension")

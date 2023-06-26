"""Serializers of the tags extension."""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from . import models

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        """Serializer settings."""

        model = models.Tag
        fields = "__all__"
        read_only_fields = ("id", "extension")


class TagHistorySerializer(serializers.ModelSerializer):
    """Serializer for tag history."""

    class Meta:
        """Serializer settings."""

        model = models.Tag.history.model
        fields = "__all__"


class TagProfileSerializer(serializers.ModelSerializer):
    """Serializer for tag profiles."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=models.Tag.objects.all()
    )

    class Meta:
        """Serializer settings."""

        label = "Tags"
        model = User
        fields = ["id", "tags"]
        read_only_fields = ["id"]

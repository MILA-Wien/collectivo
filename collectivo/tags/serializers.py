"""Serializers of the tags extension."""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from . import models


User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        """Serializer settings."""

        model = models.Tag
        fields = "__all__"
        read_only_fields = ("id", "extension")


class TagProfileSerializer(serializers.ModelSerializer):
    """Serializer for tag profiles."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=models.Tag.objects.all()
    )

    class Meta:
        """Serializer settings."""

        model = User
        fields = ["id", "tags"]
        read_only_fields = ["id"]

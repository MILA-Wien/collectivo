"""Serializers of the core extension."""
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()
Group = User.groups.field.related_model


class UserSerializer(serializers.ModelSerializer):
    """Serializer for members to manage their own data."""

    class Meta:
        """Serializer settings."""

        model = User
        fields = ["id", "first_name", "last_name", "email", "groups"]
        read_only_fields = ["id"]
        extra_kwargs = {"groups": {"label": "Permissions"}}


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for members to manage their own data."""

    class Meta:
        """Serializer settings."""

        model = Group
        fields = ["name"]

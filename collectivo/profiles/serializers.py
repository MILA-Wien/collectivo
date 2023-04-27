"""Serializers of the profiles extension."""

from rest_framework import serializers

from collectivo.utils.serializers import UserFields, UserIsPk

from . import models

conditions = {
    "natural": {
        "field": "person_type",
        "condition": "exact",
        "value": "natural",
    },
    "legal": {"field": "person_type", "condition": "exact", "value": "legal"},
}


class ProfileBaseSerializer(UserIsPk, UserFields):
    """Base serializer for member serializers with extra schema attributes."""

    schema_attrs = {
        "birthday": {"condition": conditions["natural"], "required": True},
        "occupation": {"condition": conditions["natural"], "required": True},
        "legal_name": {"condition": conditions["legal"], "required": True},
        "legal_type": {"condition": conditions["legal"], "required": True},
        "legal_id": {"condition": conditions["legal"], "required": True},
    }


class ProfileAdminSerializer(ProfileBaseSerializer):
    """Serializer for admins to manage members."""

    # Display user as id so that the frontend always gets an id field
    id = serializers.SerializerMethodField()

    user__tags = serializers.PrimaryKeyRelatedField(
        many=True,
        source="user.tags",
        read_only=True,
        label="Tags",
    )

    class Meta:
        """Serializer settings."""

        model = models.UserProfile
        fields = "__all__"
        read_only_fields = ["user"]


class ProfileUserSerializer(ProfileBaseSerializer):
    """Serializer for members to manage their own data."""

    class Meta:
        """Serializer settings."""

        model = models.UserProfile
        exclude = ["user", "notes"]

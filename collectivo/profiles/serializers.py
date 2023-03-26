"""Serializers of the profiles extension."""

from rest_framework import serializers

from . import models

conditions = {
    "sepa": {
        "field": "shares_payment_type",
        "condition": "exact",
        "value": "sepa",
    },
    "natural": {
        "field": "person_type",
        "condition": "exact",
        "value": "natural",
    },
    "legal": {"field": "person_type", "condition": "exact", "value": "legal"},
}


class ProfileBaseSerializer(serializers.ModelSerializer):
    """Base serializer for member serializers with extra schema attributes."""

    # Display user fields on the same level as member fields
    user__first_name = serializers.CharField(
        source="user.first_name", read_only=True, label="First name"
    )
    user__last_name = serializers.CharField(
        source="user.last_name", read_only=True, label="Last name"
    )
    user__email = serializers.EmailField(
        source="user.email", read_only=True, label="Email"
    )

    schema_attrs = {
        "birthday": {"condition": conditions["natural"], "required": True},
        "occupation": {"condition": conditions["natural"], "required": True},
        "legal_name": {"condition": conditions["legal"], "required": True},
        "legal_type": {"condition": conditions["legal"], "required": True},
        "legal_id": {"condition": conditions["legal"], "required": True},
    }

    def get_id(self, obj):
        """Return user id."""
        return obj.user.id


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


class ProfileUserSerializer(ProfileBaseSerializer):
    """Serializer for members to manage their own data."""

    class Meta:
        """Serializer settings."""

        model = models.UserProfile
        exclude = ["user", "notes"]

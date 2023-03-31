"""Serializer utilities for collectivo."""
from rest_framework import serializers


class UserIsPk(serializers.ModelSerializer):
    """Serializer for models with user as primary key with user id as id."""

    id = serializers.SerializerMethodField()

    def get_id(self, obj):
        """Return user id."""
        return obj.user.id


class UserFields(serializers.ModelSerializer):
    """Serializer for models with user relation with user fields as fields."""

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

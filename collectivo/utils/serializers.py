"""Serializer utilities for collectivo."""
from rest_framework import serializers


class UserPkModelSerializer(serializers.ModelSerializer):
    """Base serializer for models that have a user as primary key."""

    # Display user as id so that the frontend always gets an id field
    id = serializers.SerializerMethodField()

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

    def get_id(self, obj):
        """Return user id."""
        return obj.user.id

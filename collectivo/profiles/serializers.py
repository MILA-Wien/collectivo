"""Serializers of the profiles extension."""

from rest_framework import serializers

from collectivo.utils.schema import Schema
from collectivo.utils.serializers import UserIsPk

from . import models

conditions = {
    "natural": {
        "field": "person_type",
        "condition": "equals",
        "value": "natural",
    },
    "legal": {"field": "person_type", "condition": "equals", "value": "legal"},
}


schema: Schema = {
    "actions": ["retrieve", "update"],
    "fields": {
        "person_type": {"required": True},
        "user__first_name": {"label": "First name", "input_type": "text"},
        "user__last_name": {"label": "Last name", "input_type": "text"},
        "birthday": {"visible": conditions["natural"], "required": True},
        "occupation": {"visible": conditions["natural"], "required": True},
        "legal_name": {"visible": conditions["legal"], "required": True},
        "legal_type": {"visible": conditions["legal"], "required": True},
        "legal_id": {"visible": conditions["legal"], "required": True},
    },
    "structure": [
        {
            "fields": ["person_type"],
        },
        {
            "label": "Personal details",
            "visible": conditions["natural"],
            "fields": [
                "user__first_name",
                "user__last_name",
                "gender",
                "birthday",
                "occupation",
            ],
        },
        {
            "label": "Contact person",
            "visible": conditions["legal"],
            "fields": ["user__first_name", "user__last_name", "gender"],
        },
        {
            "label": "Organization details",
            "visible": conditions["legal"],
            "fields": ["legal_name", "legal_type", "legal_id"],
        },
        {
            "label": "Address",
            "fields": [
                "address_street",
                "address_number",
                "address_stair",
                "address_door",
            ],
        },
        {"fields": ["address_postcode", "address_city", "address_country"]},
        {
            "fields": [
                "phone",
            ],
        },
    ],
}


class ProfileBaseSerializer(UserIsPk):
    """Base serializer for member serializers with extra schema attributes."""


class ProfileAdminSerializer(ProfileBaseSerializer):
    """Serializer for admins to manage profiles."""

    class Meta:
        """Serializer settings."""

        label = "Profile"
        model = models.UserProfile
        fields = "__all__"
        read_only_fields = ["user"]
        schema = schema


class ProfileHistorySerializer(ProfileBaseSerializer):
    """Serializer for admins to manage profile history."""

    class Meta:
        """Serializer settings."""

        label = "Profile"
        model = models.UserProfile.history.model
        fields = "__all__"


class ProfileRegisterSerializer(serializers.ModelSerializer):
    """Serializer for users to manage their own profile."""

    user__first_name = serializers.CharField(
        source="user.first_name", required=False
    )
    user__last_name = serializers.CharField(
        source="user.last_name", required=False
    )

    class Meta:
        """Serializer settings."""

        label = "Profile"
        model = models.UserProfile
        exclude = ["user", "notes"]
        schema = schema

    def update(self, instance, validated_data):
        """Update user fields seperately."""
        user_fields = validated_data.pop("user")
        obj = super().update(instance, validated_data)
        for key, value in user_fields.items():
            setattr(obj.user, key, value)
            obj.user.save()
        return obj


class ProfileUserSerializer(serializers.ModelSerializer):
    """Serializer for members to manage their own data."""

    class Meta:
        """Serializer settings."""

        label = "Profile"
        model = models.UserProfile
        exclude = ["user", "notes"]
        schema = schema

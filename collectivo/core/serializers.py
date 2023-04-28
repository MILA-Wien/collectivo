"""Serializers of the core extension."""
from django.contrib.auth import get_user_model
from rest_framework import serializers
from collectivo.profiles.models import UserProfile
from collectivo.payments.models import PaymentProfile
from mila.registration.models import SurveyProfile
from django.db import models

User = get_user_model()
Group = User.groups.field.related_model
serializer_field_mapping = serializers.ModelSerializer.serializer_field_mapping


class UserSerializer(serializers.ModelSerializer):
    """Serializer for members to manage their own data."""

    class Meta:
        """Serializer settings."""

        model = User
        fields = ["id", "first_name", "last_name", "email", "groups"]
        read_only_fields = ["id"]
        extra_kwargs = {"groups": {"label": "Permissions"}}


class UserProfilesSerializer(serializers.ModelSerializer):
    """Serializer of user, including all profiles."""

    # tags = serializers.MultipleChoiceField(
    #     source=f"tags",
    #     read_only=True,
    #     many=True,
    # )

    profiles = [UserProfile, PaymentProfile]  # , SurveyProfile]
    for profile in profiles:
        _related_name = profile._meta.get_field("user")._related_name
        for field in profile._meta.get_fields():
            _field_class = serializer_field_mapping.get(field.__class__)
            if _field_class:
                locals()[f"{_related_name}__{field.attname}"] = _field_class(
                    source=f"{_related_name}.{field.attname}",
                    read_only=True,
                )
            elif field.__class__ is models.ManyToManyField:
                locals()[
                    f"{_related_name}__{field.attname}"
                ] = serializers.MultipleChoiceField(
                    source=f"{_related_name}.{field.attname}",
                    read_only=True,
                    many=True,
                )

    class Meta:
        """Serializer settings."""

        model = User
        exclude = ["password"]
        read_only_fields = ["user"]


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for members to manage their own data."""

    class Meta:
        """Serializer settings."""

        model = Group
        fields = ["name"]

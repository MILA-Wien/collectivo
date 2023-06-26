"""Serializers of the core extension."""
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.module_loading import import_string
from rest_framework import serializers

from collectivo.utils.schema import SchemaCondition

from .models import CoreSettings, Permission, PermissionGroup

User = get_user_model()
Group = User.groups.field.related_model
serializer_field_mapping = serializers.ModelSerializer.serializer_field_mapping
logger = logging.getLogger(__name__)


class CoreSettingsSerializer(serializers.ModelSerializer):
    """Serializer for core settings."""

    class Meta:
        """Serializer settings."""

        label = "Core Settings"
        model = CoreSettings
        exclude = ["id"]


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for permissions."""

    class Meta:
        """Serializer settings."""

        model = Permission
        fields = "__all__"


if_extension: SchemaCondition = {
    "condition": "not_empty",
    "field": "extension",
}

if_not_users_custom: SchemaCondition = {
    "condition": "equals",
    "field": "users_custom",
    "value": False,
}

if_not_perms_custom: SchemaCondition = {
    "condition": "equals",
    "field": "perms_custom",
    "value": False,
}


class PermissionGroupSerializer(serializers.ModelSerializer):
    """Serializer for permission groups."""

    class Meta:
        """Serializer settings."""

        model = PermissionGroup
        fields = "__all__"
        read_only_fields = ["extension"]

        schema_attrs = {
            "name": {"read_only": if_extension},
            "extension": {"visible": if_extension},
            "description": {"read_only": if_extension},
            "perms_custom": {"visible": False},
            "permissions": {"read_only": if_not_perms_custom},
            "users_custom": {"visible": False},
            "users": {"read_only": if_not_users_custom},
        }


class PermissionGroupHistorySerializer(serializers.ModelSerializer):
    """Serializer for history of permission groups."""

    class Meta:
        """Serializer settings."""

        model = PermissionGroup.history.model
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    """Serializer for users."""

    permission_groups = serializers.PrimaryKeyRelatedField(
        many=True, queryset=PermissionGroup.objects.all()
    )

    class Meta:
        """Serializer settings."""

        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "permission_groups",
        ]
        read_only_fields = ["id"]


class UserHistorySerializer(serializers.ModelSerializer):
    """Serializer for history of users."""

    class Meta:
        """Serializer settings."""

        model = User.history.model
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for members to manage their own data."""

    # TODO: Display all permissions of the user based on their groups
    # permissions = serializers.PrimaryKeyRelatedField(
    #     many=True, queryset=Permission.objects.all()
    # )
    permissions = serializers.SerializerMethodField()

    def get_permissions(self, obj):
        """Return permissions of the user."""
        perms = {}
        for name, ext in Permission.objects.filter(
            groups__in=obj.permission_groups.all()
        ).values_list("name", "extension__name"):
            if ext in perms:
                perms[ext].append(name)
            else:
                perms[ext] = [name]
        return perms

    class Meta:
        """Serializer settings."""

        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "permissions",
        ]
        read_only_fields = ["first_name", "last_name"]
        extra_kwargs = {"password": {"write_only": True, "required": False}}


profile_serializers = [
    import_string(ext["user_admin_serializer"])
    for ext in settings.COLLECTIVO["extensions"].values()
    if "user_admin_serializer" in ext
]


class UserProfilesSerializer(serializers.ModelSerializer):
    """Serializer of user, including the fields of all profiles."""

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()

    # TODO: Load through TagProfile
    tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    # Define serializer fields based on registered profiles in store
    # TODO: Get field settings from serializer
    # TODO: Make fields editable for bulk edit

    for profile_serializer in profile_serializers:
        profile = profile_serializer.Meta.model
        _related_name = profile._meta.get_field("user")._related_name
        for field in profile._meta.get_fields():
            _field_class = serializer_field_mapping.get(field.__class__)
            if _field_class:
                if hasattr(field, "choices") and field.choices:
                    locals()[
                        f"{_related_name}__{field.attname}"
                    ] = serializers.ChoiceField(
                        source=f"{_related_name}.{field.attname}",
                        choices=field.choices,
                        read_only=True,
                    )
                else:
                    locals()[
                        f"{_related_name}__{field.attname}"
                    ] = _field_class(
                        source=f"{_related_name}.{field.attname}",
                        read_only=True,
                    )
            elif field.__class__ in (models.ForeignKey, models.OneToOneField):
                locals()[
                    f"{_related_name}__{field.attname}"
                ] = serializers.PrimaryKeyRelatedField(
                    source=f"{_related_name}.{field.attname}",
                    read_only=True,
                )
            elif field.__class__ is models.ManyToManyField:
                locals()[
                    f"{_related_name}__{field.attname}"
                ] = serializers.PrimaryKeyRelatedField(
                    source=f"{_related_name}.{field.attname}",
                    read_only=True,
                    many=True,
                )

    class Meta:
        """Serializer settings."""

        model = User
        exclude = [
            "username",
            "password",
            "is_superuser",
            "is_staff",
            "is_active",
            "user_permissions",
            "last_login",
            "date_joined",
            "groups",
        ]
        read_only_fields = ["user"]

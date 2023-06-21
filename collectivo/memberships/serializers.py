"""Serializers of the memberships extension."""
import logging
from types import SimpleNamespace

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from collectivo.utils.schema import Schema, SchemaCondition
from collectivo.utils.serializers import UserFields

from . import models
from .statistics import calculate_statistics

User = get_user_model()


class MembershipSerializer(UserFields):
    """Serializer for admins to manage memberships."""

    try:
        import collectivo.tags

        user__tags = serializers.PrimaryKeyRelatedField(
            many=True,
            source="user.tags",
            read_only=True,
            label="Tags",
        )
    except ImportError:
        pass
    try:
        import collectivo.profiles

        user__profile__person_type = serializers.CharField(
            source="user.profile.person_type",
            read_only=True,
            label="Person type",
        )
    except ImportError:
        pass

    class Meta:
        """Serializer settings."""

        model = models.Membership
        fields = "__all__"
        read_only_fields = ["id", "number"]
        schema_attrs = {
            "user__first_name": {"input_type": "text"},
            "user__last_name": {"input_type": "text"},
            "user__profile__person_type": {"input_type": "text"},
        }

    def validate(self, data):
        """Validate the data."""

        # Check if the date of the current stage is set
        stage = data.get("stage", None)
        if stage is not None and data.get(f"date_{stage}", None) is None:
            raise ValidationError(f"Stage '{stage} requires 'date_{stage}'")
        return data


class MembershipSelfSerializer(serializers.ModelSerializer):
    """Serializer for users to manage their own memberships."""

    class Meta:
        """Serializer settings."""

        model = models.Membership
        fields = "__all__"
        depth = 1
        label = "Membership"

    def get_fields(self):
        """Set all fields to read only except shares_signed."""
        fields = super().get_fields()
        for field_name, field in fields.items():
            if field_name != "shares_signed":
                field.read_only = True
        return fields

    def validate(self, data):
        """Validate the data."""
        if data.get("shares_signed", None) is not None:
            if data["shares_signed"] < self.instance.shares_signed:
                raise serializers.ValidationError(
                    "You cannot lower the number of shares you signed."
                )
            if self.instance.type.shares_number_custom_min is not None:
                if (
                    data["shares_signed"]
                    < self.instance.type.shares_number_custom_min
                ):
                    raise serializers.ValidationError(
                        "The number of shares you signed is too low."
                    )
            if self.instance.type.shares_number_custom_max is not None:
                if (
                    data["shares_signed"]
                    > self.instance.type.shares_number_custom_max
                ):
                    raise serializers.ValidationError(
                        "The number of shares you signed is too high."
                    )

        return data


class MembershipProfileSerializer(serializers.ModelSerializer):
    """Serializer for tag profiles."""

    memberships = serializers.PrimaryKeyRelatedField(
        many=True, queryset=models.Membership.objects.all()
    )

    class Meta:
        """Serializer settings."""

        label = "Memberships"
        model = User
        fields = ["id", "memberships"]
        read_only_fields = ["id", "memberships"]


email_fields = [
    "emails__template_started",
    "emails__template_accepted",
    "emails__template_ended",
]

if_shares: SchemaCondition = {
    "condition": "equals",
    "field": "has_shares",
    "value": True,
}
if_fees: SchemaCondition = {
    "condition": "equals",
    "field": "has_fees",
    "value": True,
}


class MembershipTypeSerializer(serializers.ModelSerializer):
    """Serializer for membership types."""

    statistics = serializers.SerializerMethodField()

    class Meta:
        """Serializer settings."""

        model = models.MembershipType
        fields = "__all__"
        read_only_fields = ["id"]
        label = "Membership type"

        schema_attrs = {
            "shares_amount_per_share": {"visible": if_shares},
            "shares_number_custom": {"visible": if_shares},
            "shares_number_custom_min": {"visible": if_shares},
            "shares_number_custom_max": {"visible": if_shares},
            "shares_number_standard": {"visible": if_shares},
            "shares_number_social": {"visible": if_shares},
            "fees_amount_custom": {"visible": if_fees},
            "fees_amount_custom_min": {"visible": if_fees},
            "fees_amount_custom_max": {"visible": if_fees},
            "fees_amount_standard": {"visible": if_fees},
            "fees_amount_social": {"visible": if_fees},
            "fees_repeat_each": {"visible": if_fees},
            "fees_repeat_unit": {"visible": if_fees},
        }

    def get_statistics(self, obj):
        """Get statistics for this membership type."""
        return calculate_statistics(obj)


class MembershipStatusSerializer(serializers.ModelSerializer):
    """Serializer for membership statuses."""

    class Meta:
        """Serializer settings."""

        model = models.MembershipStatus
        fields = "__all__"
        read_only_fields = ["id"]
        label = "Membership status"


class MembershipRegisterSerializer(serializers.ModelSerializer):
    """Serializer of serializers for membership registration."""

    class Meta:
        """Serializer settings."""

        label = "Membership"
        model = models.Membership
        fields = ["status", "shares_signed"]


logger = logging.getLogger(__name__)

try:
    registration_serializers = settings.COLLECTIVO["extensions"][
        "collectivo.memberships"
    ].get("registration_serializers", [])
    for item in registration_serializers:
        for method, serializer in item.items():
            item[method] = import_string(serializer)
except Exception as e:
    logger.error(e, exc_info=True)
    registration_serializers = []


conditions = {
    "natural": {
        "field": "person_type",
        "condition": "equals",
        "value": "natural",
    },
    "legal": {"field": "person_type", "condition": "equals", "value": "legal"},
}


schema_settings: Schema = {
    "actions": ["retrieve", "update"],
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
            "style": "row",
        },
        {
            "label": "Contact person",
            "visible": conditions["legal"],
            "fields": ["user__first_name", "user__last_name", "gender"],
            "style": "row",
        },
        {
            "label": "Organization details",
            "visible": conditions["legal"],
            "fields": ["legal_name", "legal_type", "legal_id"],
            "style": "row",
        },
        {
            "label": "Address",
            "fields": [
                "address_street",
                "address_number",
                "address_stair",
                "address_door",
                "address_postcode",
                "address_city",
                "address_country",
                "phone",
            ],
            "style": "row",
        },
    ],
}


class MembershipRegisterCombinedSerializer(serializers.Serializer):
    """Serializer of serializers for membership registration."""

    class Meta:
        """Serializer settings."""

        label = "Membership registration"
        model = models.Membership
        fields = "__all__"

    for item in registration_serializers:
        for method, serializer in item.items():
            locals()[serializer.__name__] = serializer()

    @classmethod
    def initialize(cls, membership_type, user):
        """Initialize serializer with data from database."""
        payload = SimpleNamespace()

        for item in registration_serializers:
            for method, serializer in item.items():
                name = serializer.__name__
                model = serializer.Meta.model
                if method == "update":
                    obj = model.objects.get(user=user)
                    setattr(payload, name, obj)
                else:
                    setattr(payload, name, None)

        return cls(payload)

    def to_representation(self, instance):
        """Call all serializers for registration."""
        if instance:
            return super().to_representation(instance)
        else:
            return {}

    def create(self, validated_data):
        """Call all serializers for registration."""

        request = self.context.get("request")

        for item in registration_serializers:
            for method, serializer in item.items():
                name = serializer.__name__
                data = validated_data.pop(name)
                model = serializer.Meta.model
                if method == "create":
                    model.objects.create(**data)
                elif method == "update":
                    obj = model.objects.get(user=request.user)
                    for field, value in data.items():
                        setattr(obj, field, value)
                    obj.save()

        return {}

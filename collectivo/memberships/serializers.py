"""Serializers of the memberships extension."""
import logging
from types import SimpleNamespace

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.module_loading import import_string
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from collectivo.tags.models import Tag
from collectivo.utils.schema import Schema, SchemaCondition
from collectivo.utils.serializers import UserFields

from . import models
from .statistics import calculate_statistics

User = get_user_model()

logger = logging.getLogger(__name__)


class _TagsSerializer(serializers.Serializer):
    """Serializer for tags.

    TODO: This is a temporary solution as a m2m field with source (below) is
    not writable.
    """

    user__tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        read_only=False,
    )


class MembershipSerializer(UserFields):
    """Serializer for admins to manage memberships."""

    try:
        from collectivo.tags.models import Tag

        user__tags = serializers.PrimaryKeyRelatedField(
            source="user.tags",
            queryset=Tag.objects.all(),
            label="Tags",
            many=True,
            required=False,
            allow_null=True,
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

    def update(self, instance, validated_data):
        """Save user tags seperately."""
        tr = _TagsSerializer(data=self.initial_data)
        tr.is_valid()
        if "user_tags" in tr.validated_data:
            instance.user.tags.set(tr.validated_data["user__tags"])

        return super().update(instance, validated_data)


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


# TODO Specify membership type automatically
# TODO Status only of membership type
# TODO Shares
# TODO Fees
class MembershipRegisterSerializer(serializers.ModelSerializer):
    """Serializer of serializers for membership registration."""

    class Meta:
        """Serializer settings."""

        label = "Membership"
        model = models.Membership
        fields = ["type", "status", "shares_signed"]
        schema: Schema = {
            "fields": {"status": {"required": True}},
            "type": {"visible": False},
        }

    # Add user id to data before saving
    def create(self, validated_data):
        """Add user to registration data."""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


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
        with transaction.atomic():
            request = self.context.get("request")
            for item in registration_serializers:
                for method, serializer in item.items():
                    name = serializer.__name__
                    data = request.data[name]
                    model = serializer.Meta.model
                    if method == "create":
                        seri = serializer(data=data)
                        seri.context.update({"request": request})
                        seri.is_valid(raise_exception=True)
                        seri.create(seri.validated_data)
                    elif method == "update":
                        instance = model.objects.get(user=request.user)
                        seri = serializer(instance, data=data)
                        seri.is_valid(raise_exception=True)
                        seri.update(instance, seri.validated_data)

        return {}


class MembershipHistorySerializer(serializers.ModelSerializer):
    """Serializer for membership history."""

    class Meta:
        """Serializer settings."""

        model = models.Membership.history.model
        fields = "__all__"


class MembershipTypeHistorySerializer(serializers.ModelSerializer):
    """Serializer for membershipType history."""

    class Meta:
        """Serializer settings."""

        model = models.MembershipType.history.model
        fields = "__all__"

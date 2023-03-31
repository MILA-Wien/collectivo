"""Serializers of the mila registration extension."""

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from collectivo.memberships.models import MembershipStatus, MembershipType
from collectivo.memberships.serializers import MembershipSerializer
from collectivo.payments.models import PaymentProfile
from collectivo.payments.serializers import PaymentProfileSerializer
from collectivo.profiles.models import UserProfile
from collectivo.tags.models import Tag
from collectivo.utils.serializers import UserFields, UserIsPk

from . import models


class SurveyProfileSerializer(UserIsPk, UserFields):
    """Serializer for registration surveys."""

    class Meta:
        """Serializer settings."""

        model = models.SurveyProfile
        fields = "__all__"


class SurveyGroupSerializer(serializers.ModelSerializer):
    """Serializer for registration survey groups."""

    class Meta:
        """Serializer settings."""

        model = models.SurveyGroup
        fields = "__all__"


class SurveySkillSerializer(serializers.ModelSerializer):
    """Serializer for registration survey skills."""

    class Meta:
        """Serializer settings."""

        model = models.SurveySkill
        fields = "__all__"


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


class MemberRegisterSerializer(serializers.ModelSerializer):
    """Serializer for MILA users to register as coop members."""

    def __init__(self, *args, **kwargs):
        """Fill the possible status options for Genossenschaft MILA."""
        super().__init__(*args, **kwargs)
        self.fields["membership_status"].choices = [
            (x.id, x.name) for x in MembershipStatus.objects.all()
        ]

    schema_attrs = {
        "birthday": {"condition": conditions["natural"], "required": True},
        "occupation": {"condition": conditions["natural"], "required": True},
        "legal_name": {"condition": conditions["legal"], "required": True},
        "legal_type": {"condition": conditions["legal"], "required": True},
        "legal_id": {"condition": conditions["legal"], "required": True},
        "membership_status": {
            "condition": conditions["natural"],
            "required": True,
        },
        "bank_account_owner": {
            "condition": conditions["sepa"],
            "required": True,
        },
        "bank_account_iban": {
            "condition": conditions["sepa"],
            "required": True,
        },
    }

    # User fields
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    # Membership fields for Genossenschaft MILA
    membership_shares = serializers.IntegerField(required=False)
    membership_status = serializers.ChoiceField(choices=[], required=False)

    # Tag fields
    statutes_approved = serializers.BooleanField(
        write_only=True, required=True
    )
    public_use_approved = serializers.BooleanField(
        write_only=True, required=False
    )
    shares_tarif = serializers.CharField(required=False)

    # Payment profile
    payment_method = serializers.CharField(required=False)
    bank_account_iban = serializers.CharField(required=False)
    bank_account_owner = serializers.CharField(required=False)

    # Registration survey
    survey_contact = serializers.CharField(required=False)
    survey_motivation = serializers.CharField(required=False)
    groups_interested = serializers.ListField(
        child=serializers.IntegerField(
            required=False,
        ),
        required=False,
    )
    skills = serializers.ListField(
        child=serializers.IntegerField(
            required=False,
        ),
        required=False,
    )

    class Meta:
        """Serializer settings."""

        model = UserProfile
        fields = [
            "user",
            "first_name",
            "last_name",
            "person_type",
            "gender",
            "birthday",
            "occupation",
            "address_street",
            "address_number",
            "address_stair",
            "address_door",
            "address_postcode",
            "address_city",
            "address_country",
            "phone",
            "legal_name",
            "legal_type",
            "legal_id",
            "statutes_approved",  # Tags
            "public_use_approved",  # Tags
            "shares_tarif",  # Membership
            "membership_shares",  # Membership
            "membership_status",  # Membership
            "payment_method",  # PaymentProfile
            "bank_account_iban",  # PaymentProfile
            "bank_account_owner",  # PaymentProfile
            "survey_contact",  # SurveyProfile
            "survey_motivation",  # SurveyProfile
            "groups_interested",  # SurveyProfile
            "skills",  # SurveyProfile
        ]
        read_only_fields = ["user"]

    def _convert_membership_status(self, attrs):
        """Adjust membership type based on person type. Custom for MILA."""

        pt = attrs.get("person_type")
        if pt == "natural":
            if attrs.get("membership_status") is None:
                raise ParseError(
                    "membership_status required for natural person"
                )
        elif pt == "legal":
            membership_status = MembershipStatus.objects.get(
                name="Investierend",
            )
            attrs["membership_status"] = membership_status.pk
        else:
            raise ParseError("person_type is invalid")
        return attrs

    def _convert_membership_shares(self, attrs):
        """Convert shares_tarif choice into shares_number value."""
        shares_tarif = attrs.pop("shares_tarif", None)
        if shares_tarif == "social":
            attrs["membership_shares"] = 1
        elif shares_tarif == "normal":
            attrs["membership_shares"] = 9
        elif shares_tarif == "more":
            if "membership_shares" not in attrs:
                raise ParseError("membership_shares: This field is required.")
        else:
            raise ParseError("shares_tarif: This field is incorrect.")
        return attrs

    def validate(self, attrs):
        """Validate and transform tag fields before validation."""

        # Save user data
        self.user_data = {
            "first_name": attrs.pop("first_name", None),
            "last_name": attrs.pop("last_name", None),
        }

        # Save membership data for create
        attrs = self._convert_membership_shares(attrs)
        attrs = self._convert_membership_status(attrs)
        self.membership_data = {
            "shares_signed": attrs.pop("membership_shares", None),
            "status": attrs.pop("membership_status", None),
        }

        # Save payment profile data for create
        self.payment_profile_data = {
            "payment_method": attrs.pop("payment_method", None),
            "bank_account_iban": attrs.pop("bank_account_iban", None),
            "bank_account_owner": attrs.pop("bank_account_owner", None),
        }

        # Save survey profile data for create
        self.survey_profile_data = {
            "survey_contact": attrs.pop("survey_contact", None),
            "skills": attrs.pop("skills", []),
            "groups_interested": attrs.pop("groups_interested", []),
            "survey_motivation": attrs.pop("survey_motivation", None),
        }

        # Save tag fields for create
        self.tag_fields = {
            "Satzung angenommen": attrs.pop("statutes_approved", None),
            "Öffentliche Verwendung": attrs.pop("public_use_approved", None),
        }

        # Ensure that the statutes are approved
        if self.tag_fields["Satzung angenommen"] is not True:
            raise ParseError("Satzung angenommen: This field must be True.")

        return super().validate(attrs)

    def create(self, validated_data):
        """Create member, membership, payment profile, and tags."""

        try:
            type = MembershipType.objects.get(
                name="MILA Mitmach-Supermarkt e. G."
            ).pk
        except MembershipType.DoesNotExist:
            type = MembershipType.objects.create(
                name="MILA Mitmach-Supermarkt e. G.",
            ).pk

        with transaction.atomic():
            profile = UserProfile.objects.get(user=validated_data["user"])

            if profile.user.memberships.filter(type=type).exists():
                raise ParseError("User is already a MILA e.G. member.")
            for field, value in validated_data.items():
                setattr(profile, field, value)
            profile.save()

            # Update user
            profile.user.first_name = self.user_data["first_name"]
            profile.user.last_name = self.user_data["last_name"]
            profile.user.save()

            # Create payment profile
            payment_profile = PaymentProfile.objects.get(user=profile.user)
            payment_profile_serializer = PaymentProfileSerializer(
                payment_profile,
                data={"user": profile.user.pk, **self.payment_profile_data},
            )
            payment_profile_serializer.is_valid(raise_exception=True)
            payment_profile_serializer.save()

            # Create membership
            membership_serializer = MembershipSerializer(
                data={
                    "user": profile.user.pk,
                    "type": type,
                    **self.membership_data,
                }
            )
            membership_serializer.is_valid(raise_exception=True)
            membership_serializer.save()

            # Create survey profile
            try:
                survey_profile = models.SurveyProfile.objects.get(
                    user=profile.user
                )
            except models.SurveyProfile.DoesNotExist:
                survey_profile = models.SurveyProfile.objects.create(
                    user=profile.user
                )
            survey_profile = SurveyProfileSerializer(
                survey_profile,
                data={
                    "user": profile.user.pk,
                    **self.survey_profile_data,
                },
            )
            survey_profile.is_valid(raise_exception=True)
            survey_profile.save()

            # Assign tags
            for field in ["Satzung angenommen", "Öffentliche Verwendung"]:
                value = self.tag_fields[field] or False
                if value is True:
                    tag = Tag.objects.get_or_create(name=field)[0]
                    tag.users.add(profile.user)
                    tag.save()

        user = UserProfile.objects.get(pk=profile.user.pk)
        return user

"""Serializers of the members extension."""

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from collectivo.payments.serializers import PaymentProfileSerializer
from collectivo.registration_survey.serializers import SurveyProfileSerializer
from collectivo.tags.models import Tag

from . import models


class MembershipSerializer(serializers.ModelSerializer):
    """Serializer for memberships."""

    class Meta:
        """Serializer settings."""

        model = models.Membership
        fields = [
            "id",
            "member",
            "type",
            "status",
            "shares",
        ]


class MemberBaseSerializer(serializers.ModelSerializer):
    """Base serializer for member serializers with extra schema attributes."""

    # Display user fields on the same level as member fields
    user__first_name = serializers.CharField(
        source="user.first_name", read_only=True
    )
    user__last_name = serializers.CharField(
        source="user.last_name", read_only=True
    )
    user__email = serializers.EmailField(source="user.email", read_only=True)
    user__tags = serializers.PrimaryKeyRelatedField(
        many=True,
        source="user.tags",
        read_only=True,
    )

    memberships = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    # TODO: Set conditional fields (better in META?)
    # schema_attrs = {
    #     field: settings["schema"]
    #     for field, settings in field_settings.items()
    #     if "schema" in settings
    # }


class MemberHistorySerializer(serializers.ModelSerializer):
    """Serializer for admins to manage member history."""

    class Meta:
        """Serializer settings."""

        model = models.Member.history.model
        fields = "__all__"


class MemberSerializer(MemberBaseSerializer):
    """Serializer for admins to manage members."""

    class Meta:
        """Serializer settings."""

        model = models.Member
        fields = "__all__"
        history = MemberHistorySerializer


class MemberProfileSerializer(MemberBaseSerializer):
    """Serializer for members to manage their own data."""

    class Meta:
        """Serializer settings."""

        model = models.Member
        fields = [
            "user",
            "user__first_name",
            "user__last_name",
            "user__email",
            "person_type",
            "gender",
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
        ]


class MemberRegisterSerializer(MemberBaseSerializer):
    """Serializer for users to register themselves as members.

    This is serializer is not generic, but custom for MILA.
    Automatically creates a membership for Genossenschaft MILA.
    """

    def __init__(self, *args, **kwargs):
        """Fill the possible status options for Genossenschaft MILA."""
        super().__init__(*args, **kwargs)
        self.fields["membership_status"].choices = [
            (x.id, x.name)
            for x in models.MembershipStatus.objects.filter(
                type__name="Genossenschaft MILA"
            ).all()
        ]

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

        model = models.Member
        fields = [
            "user",
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
        # TODO: This is still custom for MILA, and should be generalized

        pt = attrs.get("person_type")
        if pt == "natural":
            if attrs.get("membership_status") is None:
                raise ParseError("membership_type required for natural person")
        elif pt == "legal":
            membership_type = models.MembershipType.objects.get(
                name="Genossenschaft MILA"
            )
            membership_status = models.MembershipStatus.objects.get(
                type=membership_type,
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

        # Save membership data for create
        attrs = self._convert_membership_shares(attrs)
        attrs = self._convert_membership_status(attrs)
        self.membership_data = {
            "shares": attrs.pop("membership_shares", None),
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
            "Statuten angenommen": attrs.pop("statutes_approved", None),
            "Öffentlichkeitsarbeit": attrs.pop("public_use_approved", None),
        }

        # Ensure that the statutes are approved
        if self.tag_fields["Statuten angenommen"] is not True:
            raise ParseError("statutes_approved: This field must be True.")

        return super().validate(attrs)

    def create(self, validated_data):
        """Create member, membership, payment profile, and tags."""

        with transaction.atomic():
            member = super().create(validated_data)

            # Create membership
            membership = MembershipSerializer(
                data={
                    "member": member.pk,
                    "type": models.MembershipType.objects.get(
                        name="Genossenschaft MILA"
                    ).pk,
                    **self.membership_data,
                }
            )
            membership.is_valid(raise_exception=True)
            membership.save()

            # Create payment profile
            payment_profile = PaymentProfileSerializer(
                data={
                    "user": member.user.pk,
                    **self.payment_profile_data,
                }
            )
            payment_profile.is_valid(raise_exception=True)
            payment_profile.save()

            # Create survey profile
            survey_profile = SurveyProfileSerializer(
                data={
                    "user": member.user.pk,
                    **self.survey_profile_data,
                }
            )
            survey_profile.is_valid(raise_exception=True)
            survey_profile.save()

            # Assign tags
            for field in ["Statuten angenommen", "Öffentlichkeitsarbeit"]:
                value = self.tag_fields[field] or False
                if value is True:
                    tag = Tag.objects.get_or_create(name=field)[0]
                    tag.users.add(member.user)
                    tag.save()

        member = models.Member.objects.get(pk=member.pk)
        return member

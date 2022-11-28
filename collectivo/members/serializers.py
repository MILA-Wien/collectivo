"""Serializers of the members extension."""
from rest_framework import serializers
from .models import Member, MemberTag


# Fields for all members
editable_fields = (
    'gender',
    'email', 'phone',
    'address_street', 'address_number',
    'address_stair', 'address_door', 'address_postcode',
    'address_city', 'address_country',
)

legal_fields = ('legal_name', 'legal_type', 'legal_id')
natural_fields = ('birthday', )
sepa_fields = ('bank_account_iban', 'bank_account_owner')

registration_fields = (
    'first_name', 'last_name',
    'person_type', 'membership_start',
    'shares_number', 'shares_payment_type',
) + legal_fields + natural_fields + sepa_fields

readonly_fields = ('id', ) + registration_fields

summary_fields = (
    'id',
    'first_name', 'last_name',
    'person_type', 'membership_status',
    'membership_start',
    'membership_cancelled',
    'membership_end',
    'tags',
)
tag_fields = (
    'statutes_approved',
    'public_use_approved',
    'data_use_approved'
)

# Create conditions
schema_attrs = {}


def add_conditions(fields, condition_field, value):
    """Add conditions to schema attributes."""
    condition = {
        'field': condition_field, 'condition': 'exact', 'value': value}
    schema_attrs.update({
        attr: {'condition': condition} for attr in fields})


add_conditions(legal_fields, 'person_type', 'legal')
add_conditions(natural_fields, 'person_type', 'natural')
add_conditions(sepa_fields, 'shares_payment_type', 'sepa')


class MemberSerializer(serializers.ModelSerializer):
    """Base serializer for member serializers."""

    schema_attrs = schema_attrs


class MemberRegisterSerializer(MemberSerializer):
    """Serializer for users to register themselves as members."""

    # Tag fields
    statutes_approved = serializers.BooleanField(
        default=False, write_only=True)
    public_use_approved = serializers.BooleanField(
        default=False, write_only=True)
    data_use_approved = serializers.BooleanField(
        default=False, write_only=True)

    class Meta:
        """Serializer settings."""

        model = Member
        fields = editable_fields + registration_fields + tag_fields + ('id', )
        read_only_fields = ('id', )

    def validate(self, attrs):
        """Remove tag fields before model creation."""
        # TODO Logic for tag fields
        for field in tag_fields:
            attrs.pop(field, None)
        return super().validate(attrs)


class MemberProfileSerializer(MemberSerializer):
    """Serializer for members to manage their own data."""

    class Meta:
        """Serializer settings."""

        model = Member
        fields = registration_fields + editable_fields + readonly_fields
        read_only_fields = registration_fields + readonly_fields


class MemberSummarySerializer(MemberSerializer):
    """Serializer for admins to get member summaries."""

    class Meta:
        """Serializer settings."""

        model = Member
        fields = summary_fields


class MemberAdminSerializer(MemberSerializer):
    """Serializer for admins to manage members in detail."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, required=False, queryset=MemberTag.objects.all())

    class Meta:
        """Serializer settings."""

        model = Member
        fields = '__all__'

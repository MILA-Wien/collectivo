"""Serializers of the members extension."""
import copy

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ParseError, ValidationError

from . import models

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

field_settings = {
    # "id": {
    #     "permissions": ["read", "create", "table"],
    #     "kwargs": {
    #         "label": "Membership number",
    #         "help_text": "This number can be used to identify you.",
    #     },
    # },
    "first_name": {
        "permissions": ["read", "create", "table"],
        "kwargs": {"label": "First name", "required": True},
    },
    "last_name": {
        "permissions": ["read", "create", "table"],
        "kwargs": {"label": "Last name", "required": True},
    },
    "email": {
        "permissions": ["read", "table"],
        "kwargs": {
            "label": "Email address",
            "help_text": "The address used for communication and login.",
            "required": True,
        },
    },
    "person_type": {
        "permissions": ["read", "create", "table"],
        "kwargs": {
            "label": "Type of person",
            "help_text": "Whether you represent a natural person or "
            "a legal entity.",
            "required": True,
        },
    },
    "gender": {
        "permissions": ["read", "create", "change", "table"],
        "kwargs": {"label": "Gender", "required": True},
    },
    "birthday": {
        "permissions": ["create"],
        "kwargs": {"label": "Birthday"},
        "schema": {"condition": conditions["natural"], "required": True},
    },
    "occupation": {
        "permissions": ["read", "create", "change", "table"],
        "kwargs": {"label": "Occupation"},
        "schema": {"condition": conditions["natural"], "required": True},
    },
    "address_street": {
        "permissions": ["read", "create", "change", "table"],
        "kwargs": {"label": "Street", "required": True},
    },
    "address_number": {
        "permissions": ["read", "create", "change", "table"],
        "kwargs": {"label": "Number", "required": True},
    },
    "address_stair": {
        "permissions": ["read", "create", "change", "table"],
        "kwargs": {"label": "Stair", "allow_blank": True},
    },
    "address_door": {
        "permissions": ["read", "create", "change", "table"],
        "kwargs": {"label": "Door", "allow_blank": True},
    },
    "address_postcode": {
        "permissions": ["read", "create", "change", "table"],
        "kwargs": {"label": "Postcode", "required": True},
    },
    "address_city": {
        "permissions": ["read", "create", "change", "table"],
        "kwargs": {"label": "City", "required": True},
    },
    "address_country": {
        "permissions": ["read", "create", "change", "table"],
        "kwargs": {"label": "Country", "required": True},
        "schema": {"default": "Austria"},
    },
    "phone": {
        "permissions": ["read", "create", "change", "table"],
        "kwargs": {"label": "Phone number", "allow_blank": True},
    },
    # Legal person fields
    "legal_name": {
        "permissions": ["create", "table"],
        "kwargs": {"label": "Name of the organisation"},
        "schema": {"condition": conditions["legal"], "required": True},
    },
    "legal_type": {
        "permissions": ["create", "table"],
        "kwargs": {
            "label": "Type of the organisation",
            "help_text": "Such as company, association, or cooperative.",
        },
        "schema": {"condition": conditions["legal"], "required": True},
    },
    "legal_id": {
        "permissions": ["create", "table"],
        "kwargs": {
            "label": "Idenfication number of the organisation",
            "help_text": "Legal entity identifier or registry number.",
        },
        "schema": {"condition": conditions["legal"], "required": True},
    },
    # Membership fields
    "membership_type": {
        "permissions": ["read", "create", "table"],
        "kwargs": {
            "label": "Type of membership",
            "help_text": "Whether you are an active or investing member.",
            "required": False,
        },
        "schema": {
            "condition": conditions["natural"],
        },
    },
    "membership_start": {
        "kwargs": {
            "label": "Starting date of your membership",
        },
        "permissions": ["read", "table"],
    },
    "shares_number": {
        "permissions": ["read", "create", "table"],
        "kwargs": {
            "label": "Number of shares",
            "help_text": "The amount of shares that you own.",
            "required": False,
            "min_value": 1,
            "max_value": 100,
        },
    },
    "shares_payment_type": {
        "permissions": ["create"],
        "kwargs": {
            "required": True,
            "label": "Payment type",
            "help_text": "How you want to pay for your shares.",
        },
    },
    "bank_account_iban": {
        "permissions": ["create"],
        "kwargs": {
            "label": "Bank account number (IBAN)",
        },
        "schema": {"condition": conditions["sepa"], "required": True},
    },
    "bank_account_owner": {
        "permissions": ["create"],
        "kwargs": {
            "label": "Bank account owner",
        },
        "schema": {"condition": conditions["sepa"], "required": True},
    },
    # Registration survey fields
    "survey_contact": {
        "permissions": ["create", "table"],
        "kwargs": {"label": "How did you hear of MILA?", "allow_blank": True},
    },
    "survey_motivation": {
        "permissions": ["create", "table"],
        "kwargs": {
            "label": "What convinced you to join MILA?",
            "allow_blank": True,
        },
    },
    "groups_interested": {
        "permissions": ["create", "table"],
        "kwargs": {
            "label": "In which working group do you want to be active?",
        },
    },
    "skills": {
        "permissions": ["create", "table"],
        "kwargs": {
            "label": "What are your occupations/skills/interests?",
        },
    },
    # Table view
    "user_id": {
        "permissions": ["table"],
        "kwargs": {
            "label": "UUID",
        },
    },
    "membership_cancelled": {
        "permissions": ["table"],
        "kwargs": {
            "label": "Membership cancelled",
        },
    },
    "membership_end": {
        "permissions": ["table"],
        "kwargs": {
            "label": "Membership end",
        },
    },
    "tags": {
        "permissions": ["table"],
        "kwargs": {
            "label": "Tags",
        },
    },
    # Special boolean fields for registration
    # Will be converted to tags during validation
    "statutes_approved": {
        "permissions": ["create"],
        "kwargs": {
            "label": "Statutes approved",
            "required": True,
        },
    },
    "public_use_approved": {
        "permissions": ["create"],
        "kwargs": {
            "label": "Public use approved",
        },
    },
}

field_settings_admin_create = copy.deepcopy(field_settings)
field_settings_admin_create["shares_number"]["kwargs"]["required"] = True

# Boolean fields that will be converted to tags
register_fields = [
    f for f, s in field_settings.items() if "create" in s["permissions"]
]
profile_read_only_fields = [
    f
    for f, s in field_settings.items()
    if "read" in s["permissions"] and "change" not in s["permissions"]
]
profile_fields = [
    f
    for f, s in field_settings.items()
    if "change" in s["permissions"] or "read" in s["permissions"]
]
summary_fields = [
    f for f, s in field_settings.items() if "table" in s["permissions"]
]
register_tag_fields = ["statutes_approved", "public_use_approved"]


class MemberSerializer(serializers.ModelSerializer):
    """Base serializer for member serializers."""

    schema_attrs = {
        field: settings["schema"]
        for field, settings in field_settings.items()
        if "schema" in settings
    }


class MembershipSerializer(serializers.ModelSerializer):
    """Serializer for memberships."""

    class Meta:
        model = models.Membership
        fields = [
            "id",
            "member",
            "type",
            "status",
            "shares",
        ]


class MemberRegisterSerializer(MemberSerializer):
    """Serializer for users to register themselves as members.

    Automatically creates a membership for Genossenschaft MILA."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fill the possible status options for Genossenschaft MILA
        self.fields["membership_status"].choices = [
            (x.id, x.label)
            for x in models.MembershipStatus.objects.filter(
                type__label="Genossenschaft MILA"
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
            "statutes_approved",
            "public_use_approved",
            "shares_tarif",
            "membership_shares",
            "membership_status",
        ]
        read_only_fields = ["user"]
        # extra_kwargs = {
        #     field: field_settings[field]["kwargs"]
        #     for field in fields
        #     if field in field_settings and "kwargs" in field_settings[field]
        # }

    def _validate_membership_type(self, attrs):
        """Adjust membership type based on person type."""
        pt = attrs.get("person_type")
        if pt == "natural":
            if attrs.get("membership_type") is None:
                raise ParseError("membership_type required for natural person")
        elif pt == "legal":
            attrs["membership_type"] = "investing"
        else:
            raise ParseError("person_type is invalid")
        return attrs

    def _convert_shares_tarif(self, attrs):
        """Convert shares_tarif choice into shares_number value."""
        shares_tarif = attrs.pop("shares_tarif", None)
        if shares_tarif == "social":
            attrs["shares_number"] = 1
        elif shares_tarif == "normal":
            attrs["shares_number"] = 9
        elif shares_tarif == "more":
            if "shares_number" not in attrs:
                raise ParseError("shares_number: This field is required.")
        else:
            raise ParseError("shares_tarif: This field is incorrect.")
        return attrs

    def validate(self, attrs):
        """Validate and transform tag fields before validation."""
        for extra_field in [
            "statutes_approved",
            "public_use_approved",
            "shares_tarif",
        ]:
            attrs.pop(extra_field, None)

        self.membership_data = {
            "shares": attrs.pop("membership_shares", None),
            "status": attrs.pop("membership_status", None),
        }
        # membership = MembershipSerializer(data=self.membership_data)
        # TODO: Check if atomic
        # try:
        #     membership.is_valid(raise_exception=True)
        # except ValidationError as e:
        #     if e.detail != {"member": ["This field is required."]}:
        #         raise e

        # attrs["tags"] = []
        # for field in register_tag_fields:
        #     tag_setting = field_settings[field]
        #     tag_label = tag_setting["kwargs"]["label"]
        #     if field in attrs:
        #         value = attrs[field]
        #     else:
        #         value = False
        #     if (
        #         tag_setting["kwargs"].get("required") is True
        #         and value is not True
        #     ):
        #         raise ParseError(f"{field} must be true")
        #     attrs.pop(field, None)
        #     if value is True:
        #         tag_id = models.MemberTag.objects.get_or_create(
        #             label=tag_label
        #         )[0].id
        #         attrs["tags"].append(tag_id)
        # attrs = self._convert_shares_tarif(attrs)
        # attrs = self._validate_membership_type(attrs)
        return super().validate(attrs)

    def create(self, validated_data):
        """Create a member and a membership for Genossenschaft MILA."""

        with transaction.atomic():
            member = super().create(validated_data)
            membership = MembershipSerializer(
                data={
                    "member": member.pk,
                    "type": models.MembershipType.objects.get(
                        label="Genossenschaft MILA"
                    ).pk,
                    **self.membership_data,
                }
            )
            print(self.membership_data)
            membership.is_valid(raise_exception=True)
            highest = (
                models.Membership.objects.filter(
                    type__label="Genossenschaft MILA"
                )
                .order_by("number")
                .last()
            )
            if highest is None:
                number = 1
            else:
                number = highest.number + 1
            membership.save(number=number)

        member = models.Member.objects.get(pk=member.pk)
        return member


# class MemberRegisterSerializer(MemberSerializer):
#     """Serializer for users to register themselves as members."""

#     # Tag fields
#     statutes_approved = serializers.BooleanField(
#         write_only=True, required=True
#     )
#     public_use_approved = serializers.BooleanField(
#         write_only=True, required=False
#     )
#     shares_tarif = serializers.CharField(required=False)

#     class Meta:
#         """Serializer settings."""

#         model = models.Member
#         fields = register_fields + register_tag_fields + ["shares_tarif"]
#         read_only_fields = ["id"]  # Return the id after creation
#         extra_kwargs = {
#             field: field_settings[field]["kwargs"]
#             for field in fields
#             if field in field_settings and "kwargs" in field_settings[field]
#         }

#     def _validate_membership_type(self, attrs):
#         """Adjust membership type based on person type."""
#         pt = attrs.get("person_type")
#         if pt == "natural":
#             if attrs.get("membership_type") is None:
#                 raise ParseError("membership_type required for natural person")
#         elif pt == "legal":
#             attrs["membership_type"] = "investing"
#         else:
#             raise ParseError("person_type is invalid")
#         return attrs

#     def _convert_shares_tarif(self, attrs):
#         """Convert shares_tarif choice into shares_number value."""
#         shares_tarif = attrs.pop("shares_tarif", None)
#         if shares_tarif == "social":
#             attrs["shares_number"] = 1
#         elif shares_tarif == "normal":
#             attrs["shares_number"] = 9
#         elif shares_tarif == "more":
#             if "shares_number" not in attrs:
#                 raise ParseError("shares_number: This field is required.")
#         else:
#             raise ParseError("shares_tarif: This field is incorrect.")
#         return attrs

#     def validate(self, attrs):
#         """Validate and transform tag fields before validation."""
#         attrs["tags"] = []
#         for field in register_tag_fields:
#             tag_setting = field_settings[field]
#             tag_label = tag_setting["kwargs"]["label"]
#             if field in attrs:
#                 value = attrs[field]
#             else:
#                 value = False
#             if (
#                 tag_setting["kwargs"].get("required") is True
#                 and value is not True
#             ):
#                 raise ParseError(f"{field} must be true")
#             attrs.pop(field, None)
#             if value is True:
#                 tag_id = models.MemberTag.objects.get_or_create(
#                     label=tag_label
#                 )[0].id
#                 attrs["tags"].append(tag_id)
#         attrs = self._convert_shares_tarif(attrs)
#         attrs = self._validate_membership_type(attrs)
#         return super().validate(attrs)


# TODO: Fix this serializer
class MemberProfileSerializer(MemberSerializer):
    """Serializer for members to manage their own data."""

    class Meta:
        """Serializer settings."""

        model = models.Member
        fields = "__all__"  # profile_fields
        # read_only_fields = profile_read_only_fields
        # extra_kwargs = {
        #     field: field_settings[field]["kwargs"]
        #     for field in fields
        #     if field in field_settings and "kwargs" in field_settings[field]
        # }


class MemberSerializer(MemberSerializer):
    """Serializer for admins to manage members in detail."""

    # Display user fields on the same level as member fields
    user__first_name = serializers.CharField(
        source="user.first_name", read_only=True
    )
    user__last_name = serializers.CharField(
        source="user.last_name", read_only=True
    )
    user__email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        """Serializer settings."""

        model = models.Member
        fields = "__all__"


# TODO
# class MemberAdminCreateSerializer(MemberRegisterSerializer):
#     """Serializer for admins to register new members."""

#     class Meta:
#         """Serializer settings."""

#         model = models.Member
#         fields = register_fields + register_tag_fields + ["email"]
#         read_only_fields = ["id", "user_id"]  # Return the id after creation
#         extra_kwargs = {
#             field: field_settings_admin_create[field]["kwargs"]
#             for field in fields
#             if field in field_settings_admin_create
#             and "kwargs" in field_settings_admin_create[field]
#         }

#     def _convert_shares_tarif(self, attrs):
#         """Do not use shares_tarif."""
#         if "shares_number" not in attrs:
#             raise ParseError("shares_number: This field is required.")
#         return attrs

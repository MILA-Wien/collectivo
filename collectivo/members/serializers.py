"""Serializers of the members extension."""
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from . import models

conditions = {
    'sepa': {
        'field': 'shares_payment_type',
        'condition': 'exact',
        'value': 'sepa'
    },
    'natural': {
        'field': 'person_type',
        'condition': 'exact',
        'value': 'natural'
    },
    'legal': {
        'field': 'person_type',
        'condition': 'exact',
        'value': 'legal'
    },
}

field_settings = {
    'id': {
        'permissions': ['read', 'create', 'table'],
        'kwargs': {
            'label': 'Membership number',
            'help_text': 'This number can be used to identify you.',
        },
    },
    'email': {
        'permissions': ['read', 'table'],
        'kwargs': {
            'label': 'Email address',
            'help_text': 'The address used for communication and login.',
        },
    },
    'person_type': {
        'permissions': ['create', 'table'],
        'kwargs': {
            'label': 'Type of person',
            'help_text': 'Whether you represent a natural person or '
                         'a legal entity.',
            'required': True
        },
    },
    'first_name': {
        'permissions': ['read', 'create', 'table'],
        'kwargs': {'label': 'First name', 'required': True},
    },
    'last_name': {
        'permissions': ['read', 'create', 'table'],
        'kwargs': {'label': 'Last name', 'required': True},
    },
    'gender': {
        'permissions': ['read', 'create', 'change'],
        'kwargs': {'label': 'Gender', 'required': True},
    },
    'birthday': {
        'permissions': ['create'],
        'kwargs': {'label': 'Birthday'},
        'schema': {
            'condition': conditions['natural'],
            'required': True
        }
    },
    'address_street': {
        'permissions': ['read', 'create', 'change'],
        'kwargs': {'label': 'Street', 'required': True},
    },
    'address_number': {
        'permissions': ['read', 'create', 'change'],
        'kwargs': {'label': 'Number', 'required': True},
    },
    'address_stair': {
        'permissions': ['read', 'create', 'change'],
        'kwargs': {'label': 'Stair'},
    },
    'address_door': {
        'permissions': ['read', 'create', 'change'],
        'kwargs': {'label': 'Door'},
    },
    'address_postcode': {
        'permissions': ['read', 'create', 'change', 'table'],
        'kwargs': {'label': 'Postcode', 'required': True},
    },
    'address_city': {
        'permissions': ['read', 'create', 'change'],
        'kwargs': {'label': 'City', 'required': True},
    },
    'address_country': {
        'permissions': ['read', 'create', 'change', 'table'],
        'kwargs': {'label': 'Country', 'required': True},
        'schema': {'default': 'Austria'}
    },
    'phone': {
        'permissions': ['read', 'create', 'change'],
        'kwargs': {'label': 'Phone number'},
    },

    # Legal person fields
    'legal_name': {
        'permissions': ['create'],
        'kwargs': {'label': 'Name of the organisation'},
        'schema': {
            'condition': conditions['legal'],
            'required': True
        }
    },
    'legal_type': {
        'permissions': ['create'],
        'kwargs': {
            'label': 'Type of the organisation',
            'help_text': 'Such as company, association, or cooperative.'
        },
        'schema': {
            'condition': conditions['legal'],
            'required': True
        }
    },
    'legal_id': {
        'permissions': ['create'],
        'kwargs': {
            'label': 'Idenfication number of the organisation',
            'help_text': 'Legal entity identifier or registry number.'
        },
        'schema': {
            'condition': conditions['legal'],
            'required': True
        }
    },

    # Membership fields
    'membership_type': {
        'permissions': ['create', 'table'],
        'kwargs': {
            'label': 'Type of membership',
            'help_text': 'Whether you are an active or investing member.'
        },
        'schema': {
            'condition': conditions['natural'],
            'required': True
        }
    },
    'membership_start': {
        'kwargs': {
            'label': 'Starting date of your membership.',
        },
        'permissions': ['read', 'table'],
    },
    'shares_number': {
        'permissions': ['read', 'create', 'table'],
        'kwargs': {
            'label': 'Number of shares',
            'help_text': 'The amount of shares that you own.',
            'required': True,
            'min_value': 1
        }
    },
    'shares_payment_type': {
        'permissions': ['create'],
        'kwargs': {
            'required': True,
            'label': 'Payment type',
            'help_text': 'How you want to pay for your shares.',
        },
    },
    'bank_account_iban': {
        'permissions': ['create'],
        'kwargs': {
            'label': 'Bank account number (IBAN)',
        },
        'schema': {
            'condition': conditions['sepa'],
            'required': True
        }
    },
    'bank_account_owner': {
        'permissions': ['create'],
        'kwargs': {
            'label': 'Bank account owner',
        },
        'schema': {
            'condition': conditions['sepa'],
            'required': True
        }
    },

    # Registration survey fields
    'survey_contact': {
        'permissions': ['create', 'table'],
        'kwargs': {
            'label': 'How did you hear of MILA?',
        },
    },
    'survey_motivation': {
        'permissions': ['create', 'table'],
        'kwargs': {
            'label': 'What convinced you to join MILA?',
        },
    },
    'groups_interested': {
        'permissions': ['create', 'table'],
        'kwargs': {
            'label': 'In which working group do you want to be active?',
        },
    },
    'skills': {
        'permissions': ['create', 'table'],
        'kwargs': {
            'label': 'What are your occupations/skills/interests?',
        },
    },

    # Table view
    'user_id': {
        'permissions': ['table'],
        'kwargs': {
            'label': 'UUID',
        },
    },
    'membership_cancelled': {
        'permissions': ['table'],
        'kwargs': {
            'label': 'Membership cancelled',
        },
    },
    'membership_end': {
        'permissions': ['table'],
        'kwargs': {
            'label': 'Membership end',
        },
    },
    'tags': {
        'permissions': ['table'],
        'kwargs': {
            'label': 'Tags',
        },
    },

    # Special boolean fields for registration
    # Will be converted to tags during validation
    # 'statutes_approved': {
    #     'permissions': ['create'],
    #     'kwargs': {
    #         'label': 'Statutes approved',
    #         'help_text': 'TEXT PENDING JULIANNA'
    #     },
    # },
    'public_use_approved': {
        'permissions': ['create'],
        'kwargs': {
            'label': 'Public use approved',
            'help_text': 'TEXT PENDING JULIANNA'
        },
    },
    'data_use_approved': {
        'permissions': ['create'],
        'kwargs': {
            'required': True,
            'label': 'Data use approved',
            'help_text': 'TEXT PENDING JULIANNA'
        },
    },
    'founding_event': {
        'permissions': ['create'],
        'kwargs': {
            'label': 'Founding event',
            'help_text': 'TEXT PENDING JULIANNA'
        },
    },
}

# Boolean fields that will be converted to tags
register_fields = [
    f for f, s in field_settings.items()
    if 'create' in s['permissions']
]
profile_read_only_fields = [
    f for f, s in field_settings.items()
    if 'read' in s['permissions']
    and 'change' not in s['permissions']
]
profile_fields = [
    f for f, s in field_settings.items()
    if 'change' in s['permissions']
    or 'read' in s['permissions']
]
summary_fields = [
    f for f, s in field_settings.items()
    if 'table' in s['permissions']
]
register_tag_fields = [
    # 'statutes_approved'
    'public_use_approved', 'data_use_approved', 'founding_event'
]


class MemberSerializer(serializers.ModelSerializer):
    """Base serializer for member serializers."""

    schema_attrs = {
        field: settings['schema']
        for field, settings in field_settings.items()
        if 'schema' in settings
    }

    def validate(self, attrs):
        """Adjust membership type based on person type."""
        if attrs.get('person_type') == 'legal':
            attrs['membership_type'] = 'investing'
        return super().validate(attrs)


class MemberRegisterSerializer(MemberSerializer):
    """Serializer for users to register themselves as members."""

    # Tag fields
    # These will change after the founding event
    # statutes_approved = serializers.BooleanField(write_only=True)
    public_use_approved = serializers.BooleanField(
        write_only=True, required=False)
    data_use_approved = serializers.BooleanField(
        write_only=True, required=True)
    founding_event = serializers.BooleanField(
        write_only=True, required=False)

    class Meta:
        """Serializer settings."""

        model = models.Member
        fields = register_fields + register_tag_fields
        read_only_fields = ['id']  # Return the id after creation
        extra_kwargs = {
            field: field_settings[field]['kwargs'] for field in fields
            if field in field_settings and 'kwargs' in field_settings[field]
        }

    def validate(self, attrs):
        """Validate and transform tag fields before validation."""
        attrs['tags'] = []
        for field in register_tag_fields:
            tag_setting = field_settings[field]
            tag_label = tag_setting['kwargs']['label']
            value = attrs[field]
            if tag_setting['kwargs'].get('required') is True \
                    and value is not True:
                raise ParseError(f'{field} must be true')
            attrs.pop(field, None)
            if value is True:
                tag_id = models.MemberTag.objects.get(label=tag_label).id
                attrs['tags'].append(tag_id)
        return super().validate(attrs)


class MemberProfileSerializer(MemberSerializer):
    """Serializer for members to manage their own data."""

    class Meta:
        """Serializer settings."""

        model = models.Member
        fields = profile_fields
        read_only_fields = profile_read_only_fields
        extra_kwargs = {
            field: field_settings[field]['kwargs'] for field in fields
            if field in field_settings and 'kwargs' in field_settings[field]
        }


class MemberSummarySerializer(MemberSerializer):
    """Serializer for admins to get member summaries."""

    class Meta:
        """Serializer settings."""

        model = models.Member
        fields = summary_fields


class MemberAdminSerializer(MemberSerializer):
    """Serializer for admins to manage members in detail."""

    class Meta:
        """Serializer settings."""

        model = models.Member
        fields = '__all__'


class MemberTagCreateSerializer(serializers.ModelSerializer):
    """Serializer for new dashboard tiles."""

    class Meta:
        """Serializer settings."""

        model = models.MemberTag
        fields = '__all__'


class MemberTagSerializer(serializers.ModelSerializer):
    """Serializer for member tags."""

    class Meta:
        """Serializer settings."""

        model = models.MemberTag
        fields = '__all__'


class MemberSkillSerializer(serializers.ModelSerializer):
    """Serializer for member skills."""

    class Meta:
        """Serializer settings."""

        model = models.MemberSkill
        fields = '__all__'


class MemberGroupSerializer(serializers.ModelSerializer):
    """Serializer for member groups."""

    class Meta:
        """Serializer settings."""

        model = models.MemberGroup
        fields = '__all__'


class MemberStatusSerializer(serializers.ModelSerializer):
    """Serializer for member status."""

    class Meta:
        """Serializer settings."""

        model = models.MemberStatus
        fields = '__all__'

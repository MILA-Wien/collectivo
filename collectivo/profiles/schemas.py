"""Schemas of the profiles extension."""
import copy

from collectivo.utils.schema import Schema

conditions = {
    "natural": {
        "field": "person_type",
        "condition": "equals",
        "value": "natural",
    },
    "legal": {"field": "person_type", "condition": "equals", "value": "legal"},
}


profile_schema: Schema = {
    "actions": ["retrieve", "update"],
    "fields": {
        "person_type": {"required": True},
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
        {
            "fields": ["notes"]
        }
    ],
}

# User endpoints cannot edit all fields (only enforced in frontend)
profile_user_schema = copy.deepcopy(profile_schema)
profile_user_schema["settings"] = {"freeze_registration_fields": True}

# User register schema includes user first and last name (used in forms)
profile_register_schema = copy.deepcopy(profile_schema)
profile_register_schema["fields"].update(
    {
        "user__first_name": {"label": "First name", "input_type": "text"},
        "user__last_name": {"label": "Last name", "input_type": "text"},
    }
)
profile_register_schema["structure"][1]["fields"] = [
    "user__first_name",
    "user__last_name",
] + profile_register_schema["structure"][1]["fields"]

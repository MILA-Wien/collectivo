"""Schema mixin for collectivo viewsets."""
from collections import OrderedDict
from dataclasses import dataclass
from typing import Literal

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from rest_framework.fields import empty
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet

# TODO Default does not work yet
# TODO Special case for user model
# TODO Group fields together?
# TODO Remove choices from schema if choices_endpoint is set,
# once implemented in frontend

field_attrs = [
    "label",
    "help_text",
    "required",
    "default",
    "max_length",
    "min_length",
    "max_value",
    "min_value",
    "read_only",
    "write_only",
    "choices",
]

input_types = {
    "CharField": "text",
    "UUIDField": "text",
    "URLField": "url",
    "ChoiceField": "select",
    "EmailField": "email",
    "IntegerField": "number",
    "FloatField": "number",
    "DateField": "date",
    "DateTimeField": "datetime",
    "BooleanField": "checkbox",
    "ManyRelatedField": "multiselect",
    "ListField": "multiselect",
    "PrimaryKeyRelatedField": "select",
    "PhoneField": "phone",
    "CountryField": "country",
    "ListSerializer": "list",
    "ImageField": "image",
}


def get_source(model: models.Model, source: str = None) -> models.Model:
    """Get the related model for a specific source."""
    if source is None:
        return model
    for related_model_name in source.split("."):
        model = model._meta.get_field(related_model_name).related_model
    return model


def get_queryset(model, source):
    """Get the queryset for a field path."""
    model = get_source(model, source)
    return model.objects.all()


def get_choices(queryset) -> OrderedDict:
    """Generate choices for a field."""
    return OrderedDict([(item.pk, item.__str__()) for item in queryset])


def get_endpoint(model: models.Model, source: str = None) -> str:
    """Get the endpoint for a model field with a specific source."""
    model = get_source(model, source)
    if model is get_user_model():
        return None  # TODO: Implement special case for user model
    app_path = reduced_path = model._meta.app_config.name
    while "." in reduced_path:
        reduced_path, _ = reduced_path.rsplit(".", 1)
        app_path = reduced_path + ":" + app_path
    try:
        return reverse(f"{app_path}:{model._meta.model_name}-list")
    except NoReverseMatch:
        return None


@dataclass
class SchemaField:
    """A field of a schema."""

    field_type: str = None
    input_type: str = None
    label: str = None
    help_text: str = None
    required: bool = None
    default: any = None
    max_length: int = None
    min_length: int = None
    max_value: int = None
    min_value: int = None
    read_only: bool = None
    write_only: bool = None
    choices: OrderedDict = None
    choices_url: str = None


@dataclass
class SchemaCondition:
    """A condition of a schema field."""

    condition: Literal["equals", "empty", "not_empty"]
    field: str = None
    value: any = None

    def to_dict(self):
        """Return condition as dict."""
        return {
            "field": self.field,
            "condition": self.condition,
            "value": self.value,
        }


def get_model_schema(self: GenericViewSet):
    """Return model schema."""
    serializer: Serializer = self.get_serializer_class()()
    data = {}
    for field_name, field_obj in serializer.fields.items():
        field_type = field_obj.__class__.__name__
        data[field_name] = field_data = {
            "field_type": field_type,
            "input_type": input_types.get(field_type, "text"),
        }

        # Convert CharField to textarea if no max_length is set (TextField)
        if field_type == "CharField" and field_obj.max_length is None:
            data[field_name]["input_type"] = "textarea"

        for attr in field_attrs:
            if hasattr(field_obj, attr):
                # Add URL path where choices can be retrieved
                if attr == "choices" and (
                    hasattr(field_obj, "child_relation")
                    or hasattr(field_obj, "get_queryset")
                ):
                    choices_url = get_endpoint(
                        self.get_serializer_class().Meta.model,
                        field_obj.source,
                    )
                    data[field_name]["choices_url"] = choices_url

                    # TODO: This should be removed once frontend uses url
                    queryset = get_queryset(
                        self.get_serializer_class().Meta.model,
                        field_obj.source,
                    )
                    value = get_choices(queryset)

                else:
                    value = getattr(field_obj, attr)
                if value is not empty and value is not None:
                    data[field_name][attr] = value

        # Add custom schema attributes from serializer
        if (
            hasattr(serializer.Meta, "schema_attrs")
            and field_name in serializer.Meta.schema_attrs
        ):
            for key, value in serializer.Meta.schema_attrs[field_name].items():
                data[field_name][key] = (
                    value.to_dict()
                    if isinstance(value, SchemaCondition)
                    else value
                )
        # Ensure that read only fields cannot be required
        if field_data.get("read_only") is True:
            field_data["required"] = False

    schema = {
        "label": serializer.Meta.label
        if hasattr(serializer.Meta, "label")
        else serializer.Meta.model.__name__,
        "description": serializer.Meta.description
        if hasattr(serializer.Meta, "description")
        else "",
        "fields": data,
    }

    return Response(schema)

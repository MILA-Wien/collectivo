"""Utilities for collectivo views."""
from collections import OrderedDict

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.decorators import action
from rest_framework.fields import empty
from rest_framework.response import Response

from collectivo.users.permissions import IsAuthenticated
from collectivo.version import __version__

# TODO Default does not work yet
# TODO Choices can be big for large datasets
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
    "PrimaryKeyRelatedField": "select",
    "PhoneField": "phone",
    "CountryField": "country",
}


class SchemaMixin:
    """Adds an action 'schema' to a viewset."""

    @extend_schema(responses={200: OpenApiResponse()})
    @action(
        detail=False,
        url_path="schema",
        url_name="schema",
        permission_classes=[IsAuthenticated],
    )
    def _schema(self, request):
        """Return model schema."""
        serializer = self.get_serializer_class()()
        data = {}
        for field_name, field_obj in serializer.fields.items():
            field_type = field_obj.__class__.__name__
            data[field_name] = field_data = {
                "field_type": field_type,
                "input_type": input_types[field_type],
            }
            # Convert CharField to textarea if no max_length is set (TextField)
            if field_type == "CharField" and field_obj.max_length is None:
                data[field_name]["input_type"] = "textarea"
            for attr in field_attrs:
                if hasattr(field_obj, attr):
                    # Get choices from model field instead of serializer
                    # This is because serializer does not always have choices
                    if attr == "choices" and hasattr(
                        field_obj, "get_queryset"
                    ):
                        model = self.get_serializer_class().Meta.model
                        field = getattr(model, field_name)
                        value = OrderedDict(
                            [
                                (
                                    field_obj.to_representation(item),
                                    field_obj.display_value(item),
                                )
                                for item in field.get_queryset()
                            ]
                        )
                    else:
                        value = getattr(field_obj, attr)
                    if value is not empty and value is not None:
                        data[field_name][attr] = value
            if (
                hasattr(serializer, "schema_attrs")
                and field_name in serializer.schema_attrs
            ):
                for key, value in serializer.schema_attrs[field_name].items():
                    data[field_name][key] = value
            # Ensure that read only fields cannot be required
            if field_data.get("read_only") is True:
                field_data["required"] = False
        return Response(data)

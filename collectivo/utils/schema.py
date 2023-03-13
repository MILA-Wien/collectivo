"""Utilities for collectivo views."""
from collections import OrderedDict

from django.db import models
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.decorators import action
from rest_framework.fields import empty
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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


def get_related_model(model: models.Model, path: str = None) -> models.Model:
    """Get the related model for a field path."""
    if path is None:
        return model
    for related_model_name in path.split("."):
        model = model._meta.get_field(related_model_name).related_model
    return model


def get_queryset_from_source(model, path):
    """Get the queryset for a field path."""
    model = get_related_model(model, path)
    return model.objects.all()


def generate_choices(queryset) -> OrderedDict:
    """Generate choices for a field."""
    return OrderedDict([(item.pk, item.__str__()) for item in queryset])


def get_endpoint_for_model(model: models.Model, path: str = None) -> str:
    """Get the endpoint for a model."""
    model = get_related_model(model, path)
    app_path = model._meta.app_config.name
    if len(app_path.split(".")) > 2:
        raise NotImplementedError("Double nested apps not supported yet.")
    if "." in app_path:
        app_path = app_path.split(".")[0] + ":" + app_path
    try:
        return reverse(f"{app_path}:{model._meta.model_name}-list")
    except NoReverseMatch:
        return None


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

                    if attr == "choices" and (
                        hasattr(field_obj, "child_relation")
                        or hasattr(field_obj, "get_queryset")
                    ):
                        queryset = get_queryset_from_source(
                            self.get_serializer_class().Meta.model,
                            field_obj.source,
                        )
                        value = generate_choices(queryset)

                        # NEW URL instead of choices
                        choices_endpoint = get_endpoint_for_model(
                            self.get_serializer_class().Meta.model,
                            field_obj.source,
                        )
                        data[field_name]["choices_endpoint"] = choices_endpoint

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

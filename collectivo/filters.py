"""Filter functions for the collectivo app."""
from django.db import models
from django_filters import FilterSet
from rest_framework import serializers

_filters = {
    "text": [
        "exact",
        "icontains",
        "istartswith",
        "iendswith",
        "contains",
        "startswith",
        "endswith",
        "isnull",
    ],
    "number": ["exact", "gt", "gte", "lt", "lte", "in", "isnull"],
    "choice": ["exact", "isnull", "in"],
    "choices": ["exact", "contains", "isnull"],
}

# Match https://www.django-rest-framework.org/api-guide/fields/
filters = {
    "BooleanField": _filters["choice"],
    "CharField": _filters["text"],
    "EmailField": _filters["text"],
    "RegexField": _filters["text"],
    "SlugField": _filters["text"],
    "URLField": _filters["text"],
    "UUIDField": _filters["text"],
    "FilePathField": _filters["text"],
    "IPAddressField": _filters["text"],
    "IntegerField": _filters["number"],
    "FloatField": _filters["number"],
    "DecimalField": _filters["number"],
    "DateTimeField": _filters["number"],
    "DateField": _filters["number"],
    "TimeField": _filters["number"],
    "DurationField": _filters["number"],
    "ChoiceField": _filters["choice"],
    "MultipleChoiceField": _filters["choices"],
}


def get_filterset_fields(serializer: serializers.Serializer) -> dict:
    """Return a dict of filterset fields for a model."""
    return {
        name: filters[type(instance).__name__]
        for name, instance in serializer().fields.items()
        if type(instance).__name__ in filters
    }


def get_filterset_class(model_class: models.Model) -> type:
    """Return a filterset class for a model."""

    class CustomFilterSet(FilterSet):
        """A custom filterset class for a model."""

        class Meta:
            """Meta class for the filterset."""

            model = model_class
            fields = get_filterset_fields(model_class)

    return CustomFilterSet

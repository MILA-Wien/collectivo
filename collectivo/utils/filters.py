"""Filter functions for the collectivo app."""
from django.db import models
from django.db.models.fields.related import ManyToManyRel
from django_filters import FilterSet, ModelMultipleChoiceFilter
from django_filters.filterset import remote_queryset
from rest_framework import serializers

_filters = {
    "text": [
        "exact",
        # "icontains",
        # "istartswith",
        # "iendswith",
        # "contains",
        # "startswith",
        # "endswith",
        # "isnull",
    ],
    "number": ["exact", "gt", "gte", "lt", "lte", "in", "isnull"],
    "choice": ["exact", "isnull", "in"],
    "choices": ["exact", "isnull"],
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
    "PrimaryKeyRelatedField": _filters["choice"],
    "ManyRelatedField": _filters["choices"],
}


def get_ordering_fields(serializer: serializers.Serializer) -> list:
    """Return a list of fields for a serializer for ordering."""
    return [
        name
        for name, instance in serializer().fields.items()
        if not instance.write_only
    ]


def get_filterset_fields(serializer: serializers.Serializer) -> dict:
    """Return a dict of filterset fields for a serializer."""
    return {
        name: filters[type(instance).__name__]
        for name, instance in serializer().fields.items()
        if type(instance).__name__ in filters and not instance.write_only
    }


def get_filterset(serializer: serializers.Serializer) -> type:
    """Return a filterset class for a model."""

    class CustomFilterSet(FilterSet):
        """A custom filterset class for a model."""

        class Meta:
            """Meta class for the filterset."""

            model = serializer.Meta.model
            fields = get_filterset_fields(serializer)

            # Use AND logic for multiple filters of many to many relations
            filter_overrides = {
                models.ManyToManyField: {
                    "filter_class": ModelMultipleChoiceFilter,
                    "extra": lambda f: {
                        "queryset": remote_queryset(f),
                        "conjoined": True,
                    },
                },
                ManyToManyRel: {
                    "filter_class": ModelMultipleChoiceFilter,
                    "extra": lambda f: {
                        "queryset": remote_queryset(f),
                        "conjoined": True,
                    },
                },
            }

    return CustomFilterSet

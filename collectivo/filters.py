"""Filter functions for the collectivo app."""
from django.db import models
from django.db.models import Lookup


class IsNull(Lookup):
    lookup_name = "ne"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return lhs in ()


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

filters = {
    "BigAutoField": _filters["number"],
    "UUIDField": _filters["text"],
    "CharField": _filters["text"],
    "ForeignKey": _filters["choice"],
    "DateField": _filters["number"],
    "IntegerField": _filters["number"],
    "TextField": _filters["text"],
    "ManyToManyField": _filters["choices"],
    "EmailField": _filters["text"],
    "BooleanField": _filters["choice"],
    "DecimalField": _filters["number"],
    "FloatField": _filters["number"],
    "PositiveIntegerField": _filters["number"],
    "PositiveSmallIntegerField": _filters["number"],
    "SmallIntegerField": _filters["number"],
    "TimeField": _filters["number"],
    "URLField": _filters["text"],
    "GenericIPAddressField": _filters["text"],
    "SlugField": _filters["text"],
    "FileField": _filters["text"],
    "ImageField": _filters["text"],
    "DateTimeField": _filters["number"],
    "DurationField": _filters["number"],
    "BinaryField": _filters["text"],
}


def get_filterset_fields(model: models.Model) -> dict:
    """Return a dict of filterset fields for a model."""
    return {
        field.name: filters[field.get_internal_type()]
        for field in model._meta.get_fields()
    }

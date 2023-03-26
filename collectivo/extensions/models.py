"""Models of the extensions module."""
from django.db import models

from collectivo.utils.models import RegisterMixin


class Extension(models.Model, RegisterMixin):
    """An extension of collectivo."""

    name = models.CharField(max_length=255, unique=True)
    version = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        """Return string representation of the model."""
        return self.name

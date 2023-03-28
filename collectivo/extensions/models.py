"""Models of the extensions module."""
from django.db import models

from collectivo.utils.models import RegisterMixin


class Extension(models.Model, RegisterMixin):
    """An extension that can add additional functionalities to collectivo."""

    name = models.CharField(
        max_length=255, unique=True, help_text="Unique name of the extension."
    )
    label = models.CharField(
        max_length=255, blank=True, help_text="Label to display the extension."
    )
    description = models.TextField(
        blank=True, help_text="Description of the extension and its features."
    )
    built_in = models.BooleanField(
        default=False, help_text="Whether the extension is part of collectivo."
    )
    version = models.CharField(
        max_length=255, blank=True, help_text="Version of the extension."
    )
    active = models.BooleanField(
        default=True, help_text="Whether the extension is active."
    )

    def __str__(self):
        """Return string representation of the model."""
        return self.name

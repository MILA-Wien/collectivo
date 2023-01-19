"""Models of the extensions module."""
from django.db import models


class Extension(models.Model):
    """An extension of collectivo."""

    name = models.CharField(max_length=255, unique=True, primary_key=True)
    version = models.CharField(max_length=255, blank=True)
    built_in = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __str__(self):
        """Return string representation of the model."""
        return f'Extension ({self.name})'

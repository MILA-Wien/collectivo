"""Models of the extensions module."""
from django.db import models
from collectivo.models import RegisterMixin


class Extension(models.Model, RegisterMixin):
    """An extension of collectivo."""

    name = models.CharField(max_length=255, unique=True)
    version = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        """Return string representation of the model."""
        version_string = f" v{self.version}" if self.version else ""
        return f"{self.name}{version_string}"

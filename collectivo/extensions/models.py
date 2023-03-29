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

    @classmethod
    def register(cls, name: str, *args, **kwargs):
        """
        Register an extension.

        If an extension with that name already exists, it is updated.

        If no label is passed, the title-cased name is used as the label.

        If the extension is built-in, the version is set to an empty string,
        since it has no version apart from the collectivo version.

        If the name has a dot (.), it is assumed to be a module name and the
        last part is used as the name of the extension.
        """
        name = name.split(".")[-1]
        if "label" not in kwargs:
            kwargs["label"] = name.title()
        if "built_in" in kwargs and kwargs["built_in"]:
            kwargs["version"] = ""
        return super().register(name, *args, **kwargs)

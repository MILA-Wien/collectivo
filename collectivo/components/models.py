"""Models of the components module."""
from django.db import models

from collectivo.utils.managers import NameManager
from collectivo.utils.texts import EXTENSION_HELP_TEXT


class Component(models.Model):
    """A frontend component."""

    objects = NameManager()
    name = models.CharField(
        max_length=255, unique=True, help_text="Unique name of the component."
    )
    description = models.TextField(
        blank=True, help_text="Description of the component and its features."
    )
    type = models.CharField(
        max_length=255,
        help_text="Type of the component.",
        choices=(
            ("remote", "Remote Entry"),
            ("iframe", "Iframe"),
        ),
    )
    path = models.URLField(
        blank=True,
        help_text="URL of the remote entry point or iframe link.",
    )
    extension = models.ForeignKey(
        "extensions.Extension",
        on_delete=models.CASCADE,
        related_name="ux_components",
        null=True,
        blank=True,
        help_text=EXTENSION_HELP_TEXT,
    )

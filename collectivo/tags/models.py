"""Models of the tags extension."""
from django.contrib.auth import get_user_model
from django.db import models
from simple_history.models import HistoricalRecords

from collectivo.utils.texts import EXTENSION_HELP_TEXT


class TagCategory(models.Model):
    """A category of tags."""

    name = models.CharField(max_length=255, unique=True)
    extension = models.ForeignKey(
        "extensions.Extension",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text=EXTENSION_HELP_TEXT,
    )

    history = HistoricalRecords()

    def __str__(self):
        """Return string representation."""
        return self.name


class Tag(models.Model):
    """A tag that can be assigned to users."""

    name = models.CharField(max_length=255, unique=True)
    users = models.ManyToManyField(
        get_user_model(), related_name="tags", blank=True
    )
    category = models.ForeignKey(
        "TagCategory", null=True, blank=True, on_delete=models.PROTECT
    )
    extension = models.ForeignKey(
        "extensions.Extension",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text=EXTENSION_HELP_TEXT,
    )

    history = HistoricalRecords()

    def __str__(self):
        """Return string representation."""
        return self.name

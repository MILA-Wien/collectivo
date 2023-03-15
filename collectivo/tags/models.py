"""Models of the members extension."""
from django.contrib.auth import get_user_model
from django.db import models


class TagCategory(models.Model):
    """A category of tags."""

    name = models.CharField(max_length=255, unique=True)
    extension = models.ForeignKey(
        "extensions.Extension",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="The extension that this tag category belongs to.",
    )

    def __str__(self):
        """Return string representation."""
        return self.name


class Tag(models.Model):
    """A tag that can be assigned to users."""

    name = models.CharField(max_length=255, unique=True)
    users = models.ManyToManyField(get_user_model(), related_name="tags")
    category = models.ForeignKey(
        "TagCategory", null=True, blank=True, on_delete=models.CASCADE
    )
    extension = models.ForeignKey(
        "extensions.Extension",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="The extension that this tag belongs to.",
    )

    def __str__(self):
        """Return string representation."""
        return self.name

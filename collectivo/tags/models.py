"""Models of the members extension."""
from django.contrib.auth import get_user_model
from django.db import models


class TagCategory(models.Model):
    """A category of tags."""

    label = models.CharField(max_length=255, unique=True)
    from_extension = models.ForeignKey(
        "extensions.Extension", null=True, blank=True, on_delete=models.CASCADE
    )

    def __str__(self):
        """Return string representation."""
        return self.label


class Tag(models.Model):
    """A tag that can be assigned to users."""

    label = models.CharField(max_length=255, unique=True)
    users = models.ManyToManyField(get_user_model(), blank=True)
    category = models.ForeignKey("TagCategory", on_delete=models.CASCADE)
    from_extension = models.ForeignKey(
        "extensions.Extension", null=True, blank=True, on_delete=models.CASCADE
    )

    def __str__(self):
        """Return string representation."""
        return self.label

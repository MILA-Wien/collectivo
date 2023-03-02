"""Models of the dashboard extension."""
from django.db import models

from collectivo.extensions.models import Extension
from collectivo.utils import get_instance
from collectivo.utils.models import RegisterMixin


class DashboardTile(models.Model, RegisterMixin):
    """A component that can be included in the dashboard."""

    class Meta:
        unique_together = ("name", "extension")

    name = models.CharField(max_length=255, unique=True)
    label = models.CharField(max_length=255, null=True)
    extension = models.ForeignKey(
        "extensions.Extension", on_delete=models.CASCADE
    )
    component_name = models.CharField(max_length=255)
    order = models.FloatField(default=1)
    requires_group = models.ForeignKey(
        "auth.Group", on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        """Return string representation of the model."""
        return self.name

    @classmethod
    def register(
        cls,
        name: str,
        extension: str | Extension,
        **payload,
    ):
        """Register a new dashboard tile."""
        payload["extension"] = get_instance(Extension, extension)

        return super().register(name=name, **payload)

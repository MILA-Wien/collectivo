"""Models of the dashboard extension."""
from django.db import models

from collectivo.extensions.models import Extension
from collectivo.users.models import Role
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
    required_role = models.ForeignKey(
        "users.Role",
        null=True,
        on_delete=models.SET_NULL,
        related_name="required_role",
    )
    blocked_role = models.ForeignKey(
        "users.Role",
        null=True,
        on_delete=models.SET_NULL,
        related_name="blocked_role",
    )

    def __str__(self):
        """Return string representation of the model."""
        return self.name

    @classmethod
    def register(
        cls,
        name: str,
        extension: str | Extension,
        required_role: str | Role = None,
        blocked_role: str | Role = None,
        **payload,
    ):
        """Register a new dashboard tile."""
        payload["extension"] = get_instance(Extension, extension)
        payload["required_role"] = get_instance(Role, required_role)
        payload["blocked_role"] = get_instance(Role, blocked_role)

        return super().register(name=name, **payload)

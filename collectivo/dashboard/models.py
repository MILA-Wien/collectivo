"""Models of the dashboard extension."""
from django.db import models

from collectivo.models import RegisterMixin
from collectivo.users.models import Role


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
        required_role_name: str = None,
        blocked_role_name: str = None,
        **dashboard_tile_kwargs,
    ):
        """Register a new dashboard tile."""
        if required_role_name is not None:
            dashboard_tile_kwargs[
                "required_role"
            ] = Role.objects.get_or_create(name=required_role_name)[0]
        if blocked_role_name is not None:
            dashboard_tile_kwargs["blocked_role"] = Role.objects.get_or_create(
                name=blocked_role_name
            )[0]
        return super().register(name=name, **dashboard_tile_kwargs)

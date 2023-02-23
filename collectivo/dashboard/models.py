"""Models of the dashboard extension."""
from django.db import models


class DashboardTile(models.Model):
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

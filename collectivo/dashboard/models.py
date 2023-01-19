"""Models of the dashboard extension."""
from django.db import models


class DashboardTile(models.Model):
    """A component that can be included in the dashboard."""

    tile_id = models.CharField(max_length=255, unique=True, primary_key=True)
    label = models.CharField(max_length=255, null=True)
    extension = models.ForeignKey(
        'extensions.Extension', on_delete=models.CASCADE)
    component_name = models.CharField(max_length=255)
    order = models.FloatField(default=1)
    required_role = models.CharField(max_length=255, null=True)
    blocked_role = models.CharField(max_length=255, null=True)

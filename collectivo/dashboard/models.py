"""Models of the dashboard extension."""
from django.contrib.auth.models import Group
from django.db import models
from simple_history.models import HistoricalRecords

from collectivo.extensions.models import Extension
from collectivo.utils import get_instance
from collectivo.utils.managers import NameManager
from collectivo.utils.models import RegisterMixin


class DashboardTileButton(models.Model):
    """A button that can be included in a dashboard tile."""

    objects = NameManager()
    history = HistoricalRecords()

    name = models.CharField(
        max_length=255, unique=True, null=True, default=None
    )
    label = models.CharField(max_length=255, null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    link_type = models.CharField(
        max_length=255,
        choices=[
            ("internal", "Internal link"),
            ("external", "External link"),
        ],
    )

    def __str__(self):
        """Return string representation of the model."""
        return self.label


class DashboardTile(models.Model, RegisterMixin):
    """A component that can be included in the dashboard."""

    class Meta:
        """Meta settings."""

        unique_together = ("name", "extension")

    objects = NameManager()
    history = HistoricalRecords()

    name = models.CharField(max_length=255, unique=True)
    label = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=True)
    extension = models.ForeignKey(
        "extensions.Extension",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    order = models.FloatField(default=1)
    requires_group = models.ForeignKey(
        "auth.Group",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="If set, the object will only be displayed to users with "
        "this group.",
    )

    source = models.CharField(
        max_length=255,
        choices=[
            ("db", "Content is defined in the content field of this model."),
            ("component", "Content is defined in a webcomponent."),
        ],
    )
    component = models.CharField(max_length=255, blank=True)
    content = models.TextField(
        blank=True,
        help_text="HTML content to display inside the tile.",
    )
    buttons = models.ManyToManyField(
        DashboardTileButton,
        blank=True,
        help_text="Buttons to display inside the tile.",
    )

    def __str__(self):
        """Return string representation of the model."""
        return self.name

    @classmethod
    def register(
        cls,
        name: str,
        extension: str | Extension,
        requires_group: str = None,
        **payload,
    ):
        """Register a new dashboard tile."""
        payload["extension"] = get_instance(Extension, extension)
        payload["requires_group"] = get_instance(Group, requires_group)
        return super().register(name=name, **payload)

"""Models of the dashboard extension."""
from django.db import models
from simple_history.models import HistoricalRecords

from collectivo.core.models import Permission
from collectivo.extensions.models import Extension
from collectivo.utils import get_instance
from collectivo.utils.managers import NameManager


class DashboardTileButton(models.Model):
    """A button that can be included in a dashboard tile."""

    class Meta:
        """Meta settings."""

        unique_together = ("name", "extension")

    objects = NameManager()
    history = HistoricalRecords()

    name = models.CharField(
        max_length=255, unique=True, null=True, default=None
    )
    extension = models.ForeignKey(
        "extensions.Extension",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
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


class DashboardTileManager(NameManager):
    """Manager for the model DashboardTile.

    Models must have the fields name, extension,and requires_perm.
    Requires perm should be a tuple of (perm_name, ext_name).
    """

    def register(
        cls,
        name: str,
        extension: str | Extension,
        requires_perm: tuple | Permission = None,
        **payload,
    ):
        """Register a new menu item."""
        payload["extension"] = get_instance(Extension, extension)
        payload["requires_perm"] = get_instance(
            Permission, requires_perm, needs_ext=True
        )
        return super().register(name=name, **payload)


class DashboardTile(models.Model):
    """A component that can be included in the dashboard."""

    class Meta:
        """Meta settings."""

        unique_together = ("name", "extension")

    objects = DashboardTileManager()
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
    requires_perm = models.ForeignKey(
        "core.Permission",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="requires_perm",
        help_text=(
            "If set, the object will only be displayed to users with "
            "this permission."
        ),
    )
    requires_not_perm = models.ForeignKey(
        "core.Permission",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="requires_not_perm",
        help_text=(
            "If set, the object will only be displayed to users without "
            "this permission."
        ),
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

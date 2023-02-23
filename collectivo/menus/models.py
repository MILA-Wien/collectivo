"""Models of the user experience module."""
from django.db import models
from collectivo.models import RegisterMixin


class Menu(models.Model, RegisterMixin):
    """A menu to be displayed in the user interface."""

    class Meta:
        unique_together = ("name", "extension")

    name = models.CharField(max_length=255)
    extension = models.ForeignKey(
        "extensions.Extension", on_delete=models.CASCADE
    )

    items = models.ManyToManyField("menus.MenuItem")


class MenuItem(models.Model, RegisterMixin):
    """An item to be displayed in a menu."""

    class Meta:
        unique_together = ("name", "extension")

    name = models.CharField(max_length=255)
    extension = models.ForeignKey(
        "extensions.Extension", on_delete=models.CASCADE
    )

    label = models.CharField(max_length=255)
    sub_items = models.ManyToManyField("self")
    required_role = models.ForeignKey(
        "users.Role", null=True, on_delete=models.SET_NULL
    )

    action = models.CharField(
        max_length=50,
        null=True,
        choices=[
            ("component", "component"),
            ("link", "link"),
        ],
    )
    action_target = models.CharField(
        max_length=50,
        default="main",
        choices=[("main", "main"), ("blank", "blank")],
    )
    component_name = models.CharField(max_length=255, null=True)
    link_source = models.URLField(null=True)

    order = models.FloatField(default=1)
    style = models.CharField(
        max_length=50,
        default="normal",
        choices=[
            ("normal", "normal"),
        ],
    )

    icon_name = models.CharField(max_length=255, null=True)
    icon_path = models.URLField(null=True)

    def __str__(self):
        """Return string representation of the model."""
        return f"MenuItem ({self.item_id})"

"""Models of the menus extension."""
from django.contrib.auth.models import Group
from django.db import models

from collectivo.extensions.models import Extension
from collectivo.utils import get_instance
from collectivo.utils.models import RegisterMixin


class Menu(models.Model, RegisterMixin):
    """A menu to be displayed in the user interface."""

    class Meta:
        """Model settings."""

        unique_together = ("name", "extension")

    name = models.CharField(max_length=255)
    extension = models.ForeignKey(
        "extensions.Extension", on_delete=models.CASCADE
    )

    items = models.ManyToManyField("menus.MenuItem")


class MenuItem(models.Model, RegisterMixin):
    """An item to be displayed in a menu."""

    class Meta:
        """Model settings."""

        unique_together = ("name", "extension")

    name = models.CharField(max_length=255)
    extension = models.ForeignKey(
        "extensions.Extension", on_delete=models.CASCADE
    )

    label = models.CharField(max_length=255)
    items = models.ManyToManyField("self")
    requires_group = models.ForeignKey(
        "auth.Group", on_delete=models.CASCADE, null=True
    )

    target = models.CharField(
        max_length=50,
        default="main",
        choices=[("main", "main"), ("blank", "blank")],
    )
    component = models.CharField(max_length=255, null=True)
    link = models.URLField(null=True)

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
        return f"MenuItem ({self.name})"

    @classmethod
    def register(
        cls,
        name: str,
        parent: "str | tuple | Menu | MenuItem",
        extension: str | Extension,
        requires_group: str = None,
        **payload,
    ):
        """Register a new menu item."""
        payload["extension"] = get_instance(Extension, extension)
        payload["requires_group"] = get_instance(Group, requires_group)
        item = super().register(name=name, **payload)

        if isinstance(parent, tuple):
            menu_name = parent[0]
            menu_extension_name = [1]
            parent = item.get_menu(menu_name, menu_extension_name)
        elif isinstance(parent, str):
            menu_name = parent
            menu_extension_name = "core"
            parent = item.get_menu(menu_name, menu_extension_name)
        elif isinstance(parent, Menu):
            pass
        elif isinstance(parent, MenuItem):
            pass
        else:
            raise ValueError("Invalid menu type")
        parent.items.add(item)
        parent.save()
        return item

    def get_menu(self, menu_name, extension_name="core"):
        """Add this item to a menu."""
        extension = Extension.objects.get(name=extension_name)
        menu = Menu.objects.get(name=menu_name, extension=extension)
        return menu

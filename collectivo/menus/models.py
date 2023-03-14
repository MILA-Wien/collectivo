"""Models of the menus extension."""
from django.db import models

from collectivo.extensions.models import Extension
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
        name,
        menu: str | tuple | Menu = None,
        parent_item=None,
        required_group: str = None,
        **menu_item_kwargs,
    ):
        """Register a new menu item."""
        item = super().register(
            name=name, required_role=required_group, **menu_item_kwargs
        )
        if menu is not None:
            if isinstance(menu, tuple):
                menu_name = menu[0]
                menu_extension_name = [1]
            elif isinstance(menu, Menu):
                menu_name = menu.name
                menu_extension_name = menu.extension.name
            elif isinstance(menu, str):
                menu_name = menu
                menu_extension_name = "core"
            else:
                raise ValueError("Invalid menu type")
            item.add_to_menu(menu_name, menu_extension_name)
        if parent_item is not None:
            parent_item.items.add(item)
            parent_item.save()
        return item

    def add_to_menu(self, menu_name, extension_name="core"):
        """Add this item to a menu."""
        extension = Extension.objects.get(name=extension_name)
        menu = Menu.objects.get(name=menu_name, extension=extension)
        menu.items.add(self)
        return self

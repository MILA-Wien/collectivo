"""Models of the menus extension."""
from django.db import models

from collectivo.extensions.models import Extension
from collectivo.models import RegisterMixin
from collectivo.users.models import Role


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
        menu_name=None,
        parent_item=None,
        menu_extension_name: str = "core",
        required_role_name: str = None,
        **menu_item_kwargs,
    ):
        """Register a new menu item."""
        if required_role_name is not None:
            required_role = Role.objects.get_or_create(
                name=required_role_name
            )[0]
        else:
            required_role = None
        item = super().register(
            name=name, required_role=required_role, **menu_item_kwargs
        )
        if menu_name is not None:
            item.add_to_menu(menu_name, menu_extension_name)
        if parent_item is not None:
            parent_item.sub_items.add(item)
            parent_item.save()
        return item

    def add_to_menu(self, menu_name, extension_name="core"):
        """Add this item to a menu."""
        extension = Extension.objects.get(name=extension_name)
        menu = Menu.objects.get(name=menu_name, extension=extension)
        menu.items.add(self)
        return self

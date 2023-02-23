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

    action = models.CharField(
        max_length=50,
        null=True,
        default="component",
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

    def register(
        self,
        name,
        menu_name,
        menu_extension_name="collectivo.core",
        required_role_name=None,
        **menu_item_kwargs,
    ):
        """Register a new menu item."""
        role = Role.objects.get_or_create(name=required_role_name)
        item = super().register(
            name=name, required_role=role, **menu_item_kwargs
        )
        item.add_to_menu(menu_name, menu_extension_name)

    def add_to_menu(self, menu_name, extension_name="collectivo.core"):
        """Add this item to a menu."""
        extension = Extension.objects.get(name=extension_name)
        menu = Menu.objects.get(name=menu_name, extension=extension)
        menu.items.add(self)
        return self

"""Setup function for the users module."""
from collectivo.extensions.models import Extension
from collectivo.menus.models import Menu, MenuItem
from collectivo.users.models import Role


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    name = "users"

    try:
        extension = Extension.objects.get(name=name)
    except Extension.DoesNotExist:
        extension = Extension.objects.create(
            name=name,
            built_in=True,
            description="API for user authentication.",
        )

    try:
        MenuItem.objects.get(item_id="auth_logout_button")
    except MenuItem.DoesNotExist:
        MenuItem.objects.create(
            item_id="auth_logout_button",
            menu_id=Menu.objects.get(menu_id="main_menu"),
            label="Log out",
            extension=extension,
            action="component",
            component_name="logout",
            order=99,
        )

    Role.objects.get_or_create(name="superuser")

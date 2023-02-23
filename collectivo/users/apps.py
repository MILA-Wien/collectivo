"""Configuration file for the authentication module."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


def post_migrate_callback(sender, **kwargs):
    """Initialize extension after database is ready."""
    from collectivo.extensions.models import Extension
    from collectivo.menus.models import Menu, MenuItem
    from collectivo.users.models import Role
    from .setup import create_groups_and_roles

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

    try:
        MenuItem.objects.get(item_id="auth_superuser_button")
    except MenuItem.DoesNotExist:
        MenuItem.objects.create(
            item_id="auth_superuser_button",
            menu_id=Menu.objects.get(menu_id="main_menu"),
            label="suupausa",
            extension=extension,
            action="component",
            component_name="logout",
            required_role=Role.objects.get_or_create(name="superuser")[0],
            order=99,
        )

    create_groups_and_roles()


class AuthConfig(AppConfig):
    """Configuration class of the authentication module."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "collectivo.users"

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        post_migrate.connect(post_migrate_callback, sender=self)

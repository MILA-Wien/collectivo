"""Configuration file of the user experience module."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


def post_migrate_callback(sender, **kwargs):
    """Initialize extension after database is ready."""
    from collectivo.extensions.utils import register_extension
    from collectivo.menus.utils import register_menuitem
    from collectivo.dashboard.utils import register_tile

    name = "shifts"
    description = "API for shifts extension."
    register_extension(name=name, built_in=True, description=description)

    register_menuitem(
        item_id="shifts_user_menu_item",
        menu_id="main_menu",
        label="Shifts",
        extension=name,
        action="component",
        component_name="shifts",
        required_role="shifts_user",
        order=10,
    )
    register_menuitem(
        item_id="shifts_admin_menu_item",
        menu_id="main_menu",
        label="Shifts Adminitsration",
        extension=name,
        action="component",
        component_name="admin",
        required_role="shifts_admin",
        order=10,
    )
    register_tile(
        tile_id="shifts_user_tile",
        label="Shifts",
        extension=name,
        component_name="shifts_user_tile",
        required_role="shifts_user",
    )


class ShiftsConfig(AppConfig):
    """Configuration class of the shifts extension."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "collectivo.shifts"
    label = "shifts"

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        post_migrate.connect(post_migrate_callback, sender=self)

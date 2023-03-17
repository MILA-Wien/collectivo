"""Configuration file for the  extension."""
import os
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from collectivo.version import __version__


def post_migrate_callback(sender, **kwargs):
    """Initialize extension after database is ready."""
    from collectivo.extensions.utils import register_extension
    from collectivo.menus.utils import register_menuitem
    from collectivo.dashboard.utils import register_tile

    name = "direktkredit"

    register_extension(
        name=name,
        version=__version__,
        description="An extension with integration with habitat direktkredit",
    )

    register_menuitem(
        item_id="direktkredit",
        menu_id="main_menu",
        label="Direktkredite",
        extension=name,
        action="link",
        link_source=os.environ.get("DIREKTKREDIT_SERVER_URL") + "/login-oidc",
        action_target="blank",
        order=2,
    )
    register_menuitem(
        item_id="direktkredit_admin",
        menu_id="main_menu",
        label="Direktkredite Admin",
        extension=name,
        action="link",
        link_source=os.environ.get("DIREKTKREDIT_SERVER_URL")
        + "/login-oidc-admin",
        action_target="blank",
        order=3,
    )
    register_tile(
        tile_id="direktkredit_tile",
        label="My Directkredits",
        extension=name,
        component_name="direktkredit_tile",
    )


class DirektkreditConfig(AppConfig):
    """Configuration class for the dashboard extension."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "collectivo.direktkredit"

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        post_migrate.connect(post_migrate_callback, sender=self)

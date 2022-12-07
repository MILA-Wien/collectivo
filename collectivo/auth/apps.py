"""Configuration file for the authentication module."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


def post_migrate_callback(sender, **kwargs):
    """Initialize extension after database is ready."""
    from collectivo.extensions.utils import register_extension
    from collectivo.menus.utils import register_menuitem
    from .populate import create_groups_and_roles

    name = 'auth'
    description = 'API for user authentication.'
    register_extension(name=name, built_in=True, description=description)
    register_menuitem(
        item_id='auth_logout_button',
        menu_id='main_menu',
        label='Log out',
        extension=name,
        action='component',
        component_name='logout',
        order=99
    )
    create_groups_and_roles()


class AuthConfig(AppConfig):
    """Configuration class of the authentication module."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'collectivo.auth'
    label = 'collectivo_auth'

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        post_migrate.connect(post_migrate_callback, sender=self)

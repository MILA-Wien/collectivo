"""Configuration file of the user experience module."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


def post_migrate_callback(sender, **kwargs):
    """Initialize extension after database is ready."""
    from .utils import register_menu
    from collectivo.extensions.utils import register_extension

    name = 'menus'
    description = 'API for user experience.'
    register_extension(name=name, built_in=True, description=description)
    register_menu(menu_id='main_menu', extension=name)
    register_menu(menu_id='admin_menu', extension=name)


class CollectivoUxConfig(AppConfig):
    """Configuration class of the user experience module."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'collectivo.menus'

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        post_migrate.connect(post_migrate_callback, sender=self)

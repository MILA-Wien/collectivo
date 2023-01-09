"""Configuration file of the emails module."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


def post_migrate_callback(sender, **kwargs):
    """Initialize extension after database is ready."""
    from collectivo.menus.utils import register_menuitem
    from collectivo.extensions.utils import register_extension

    name = 'emails'
    description = 'API for emails.'
    register_extension(name=name, built_in=True, description=description)

    register_menuitem(
        item_id='menus_admin_menu_item',
        menu_id='main_menu',
        label='Emails',
        extension=name,
        action='component',
        component_name='emails',
        required_role='superuser',
        order=11,
    )


class CollectivoUxConfig(AppConfig):
    """Configuration class of the emails module."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'collectivo.emails'

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        post_migrate.connect(post_migrate_callback, sender=self)

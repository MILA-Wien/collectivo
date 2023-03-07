"""Configuration file for the  extension."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from collectivo.version import __version__


def post_migrate_callback(sender, **kwargs):
    """Initialize extension after database is ready."""
    from collectivo.extensions.utils import register_extension
    from collectivo.menus.utils import register_menuitem

    name = 'direktkredit'

    register_extension(
        name=name,
        version=__version__,
        description='An extension to provide a integration with habitat direktkredit'
    )

    register_menuitem(
        item_id='direktkredit',
        menu_id='main_menu',
        label='Direktkredit',
        extension=name,
        action='link',
        link_source='http://direktkredit.local:8020',
        order=1000,
    )


class DirektkreditConfig(AppConfig):
    """Configuration class for the dashboard extension."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'collectivo.direktkredit'

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        post_migrate.connect(post_migrate_callback, sender=self)

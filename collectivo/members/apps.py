"""Configuration file for the members extension."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from collectivo.version import __version__


def post_migrate_callback(sender, **kwargs):
    """Initialize extension after database is ready."""
    from collectivo.extensions.utils import register_extension
    from collectivo.menus.utils import register_menuitem
    from collectivo.dashboard.utils import register_tile

    name = 'members'

    register_extension(
        name=name,
        version=__version__,
        description='An extension to manage member data and registration.'
    )

    register_menuitem(
        item_id='members_user_menu_item',
        menu_id='main_menu',
        label='Membership',
        extension=name,
        action='component',
        component_name='profile',
        required_role='members_user',
        order=10
    )

    register_menuitem(
        item_id='members_admin_menu_item',
        menu_id='main_menu',
        label='Members',
        extension=name,
        action='component',
        component_name='members',
        required_role='members_admin',
        order=11,
    )

    register_menuitem(
        item_id='members_tags_menu_item',
        menu_id='main_menu',
        label='Tags',
        extension=name,
        action='component',
        component_name='tags',
        required_role='members_admin',
        order=11,
    )

    register_menuitem(
        item_id='members_status_menu_item',
        menu_id='main_menu',
        label='Status',
        extension=name,
        action='component',
        component_name='status',
        required_role='members_admin',
        order=11,
    )

    register_tile(
        tile_id='members_registration_tile',
        label='Membership application',
        extension=name,
        component_name='members_registration_tile',
        blocked_role='members_user'
    )


class MembersConfig(AppConfig):
    """Configuration class for the members extension."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'collectivo.members'

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        post_migrate.connect(post_migrate_callback, sender=self)

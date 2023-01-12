"""Configuration file of the emails module."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


def post_migrate_callback(sender, **kwargs):
    """Initialize extension after database is ready."""
    from collectivo.menus.utils import register_menuitem
    from collectivo.extensions.utils import register_extension
    from .utils import register_email_design, register_email_template
    from django.conf import settings

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
        required_role='members_admin',
        order=11,
    )

    if settings.DEVELOPMENT:
        res = register_email_design(
            body='<html><body style="margin:0;padding:40px;word-spacing:'
                 'normal;background-color:#fff;">{{content}}</body></html>',
        )
        register_email_template(
            design=res.data['id'],
            subject='Test email',
            message='This is a test email addressed at {{member.first_name}}.',
        )


class CollectivoUxConfig(AppConfig):
    """Configuration class of the emails module."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'collectivo.members.emails'

    def ready(self):
        """
        Initialize app when it is ready.

        Database calls are performed after migrations, using the post_migrate
        signal. This signal only works if the app has a models.py module.
        """
        post_migrate.connect(post_migrate_callback, sender=self)

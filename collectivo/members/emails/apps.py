"""Configuration file of the emails module."""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


def post_migrate_callback(sender, **kwargs):
    """Initialize extension after database is ready."""
    from collectivo.menus.utils import register_menuitem
    from .utils import register_email_design, register_email_template
    from django.conf import settings
    import logging

    logger = logging.getLogger(__name__)
    name = 'members'

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
        try:
            res = register_email_design(
                name="Test design",
                body='<html><body style="margin:0;padding:40px;word-spacing:'
                     'normal;background-color:#fff;">{{content}}</body></html>'
            )
            register_email_template(
                name="Test template",
                design=res.data['id'],
                subject='Test email',
                body='This is a test email to {{member.first_name}}.',
            )
        except Exception as e:
            logger.debug(e)


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

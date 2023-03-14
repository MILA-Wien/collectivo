"""Setup function of the menus extension."""
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.version import __version__

from .apps import EmailsConfig


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    from django.conf import settings

    extension = Extension.register(
        name=EmailsConfig.name.split(".")[-1],
        description=EmailsConfig.description,
        version=__version__,
    )

    MenuItem.register(
        name="emails",
        label="Emails",
        extension=extension,
        component_name="dashboard",
        icon_name="pi-envelope",
        menu_name="admin",
        order=11,
    )

    # TODO: Renovate this
    if settings.DEVELOPMENT:
        pass
    #     try:
    #         res = register_email_design(
    #             name="Test design",
    #             body='<html><body style="margin:0;padding:40px;word-spacing:'
    #             'normal;background-color:#fff;">{{content}}</body></html>',
    #         )
    #         register_email_template(
    #             name="Test template",
    #             design=res.data["id"],
    #             subject="Test email",
    #             body="This is a test email to {{member.first_name}}.",
    #         )
    #     except Exception as e:
    #         logger.debug(e)

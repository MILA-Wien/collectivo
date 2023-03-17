"""Setup function of the test_extension extension."""
import os

from collectivo.dashboard.models import DashboardTile
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.version import __version__

from .apps import DirektkreditConfig


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    name = DirektkreditConfig.name.split(".")[-1]
    extension = Extension.register(
        name=name,
        description=DirektkreditConfig.description,
        version=__version__,
    )

    # User objects

    MenuItem.register(
        name="direktkredit",
        label="Direktkredite",
        menu="main",
        extension=extension,
        requires_group="collectivo.direktkredit.user",
        link=os.environ.get("DIREKTKREDIT_SERVER_URL") + "/login-oidc",
        target="blank",
    )

    DashboardTile.register(
        name="direktkredit_tile",
        label="My Directkredits",
        extension=extension,
        component_name="direktkredit_tile",
        requires_group="collectivo.direktkredit.user",
    )

    # Admin objects

    MenuItem.register(
        name="direktkredit_admin",
        label="Direktkredite Admin",
        menu="admin",
        extension=extension,
        requires_group="collectivo.direktkredit.admin",
        link=os.environ.get("DIREKTKREDIT_SERVER_URL") + "/login-oidc-admin",
        target="blank",
    )

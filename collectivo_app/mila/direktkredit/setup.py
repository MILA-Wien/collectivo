"""Setup function of the mila direktkredit extension."""
import os

from collectivo.dashboard.models import DashboardTile
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    extension = Extension.register(
        name="mila_direktkredit",
        label="MILA Direktkredit",
        description="Integration with the direct loan system from habitat.",
        version="1.0.0",
    )

    # User objects
    MenuItem.register(
        name="direktkredit",
        label="Direktkredite",
        parent="main",
        extension=extension,
        requires_group="collectivo.direktkredit.user",
        link=f"{os.environ.get('DIREKTKREDIT_SERVER_URL')}/login-oidc",
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
    # TODO Warning if os environ var is missing
    MenuItem.register(
        name="direktkredit_admin",
        label="Direct loans",
        icon_name="pi-money-bill",
        parent="admin",
        extension=extension,
        requires_group="collectivo.core.admin",
        link=os.environ.get("DIREKTKREDIT_SERVER_URL") + "/login-oidc-admin",
        target="blank",
        order=29,
    )

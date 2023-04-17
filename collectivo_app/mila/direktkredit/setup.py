"""Setup function of the mila direktkredit extension."""
import os

from collectivo.dashboard.models import DashboardTile, DashboardTileButton
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
        icon_name="pi-money-bill",
        extension=extension,
        requires_group="collectivo.direktkredit.user",
        link=f"{os.environ.get('DIREKTKREDIT_SERVER_URL')}/login-oidc",
        target="blank",
    )

    button = DashboardTileButton.objects.register(
        name="direktkredit_button",
        label="Weiter",
        link=f"{os.environ.get('DIREKTKREDIT_SERVER_URL')}/login-oidc",
        link_type="external",
    )

    tile = DashboardTile.register(
        name="direktkredit_tile",
        label="Direktkredite",
        extension=extension,
        source="db",
        content="Hier kannst du deine Direktkredite einsehen und verwalten.",
        requires_group="collectivo.direktkredit.user",
    )

    tile.buttons.set([button])

    # Admin objects
    # TODO Warning if os environ var is missing
    MenuItem.register(
        name="direktkredit_admin",
        label="Direct loans",
        icon_name="pi-money-bill",
        parent="admin",
        extension=extension,
        requires_group="collectivo.core.admin",
        link=f"{os.environ.get('DIREKTKREDIT_SERVER_URL')}/login-oidc-admin",
        target="blank",
        order=29,
    )

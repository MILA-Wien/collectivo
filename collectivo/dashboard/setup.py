"""Setup function of the dashboard extension."""
from django.conf import settings

from collectivo.dashboard.apps import DashboardConfig
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem

from .models import DashboardTile, DashboardTileButton


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    extension = Extension.register(
        name=DashboardConfig.name,
        description=DashboardConfig.description,
        built_in=True,
    )

    MenuItem.register(
        name="dashboard",
        label="Dashboard",
        extension=extension,
        component="dashboard",
        icon_name="pi-home",
        parent="main",
        order=0,
    )

    MenuItem.register(
        name="admin",
        label="Dashboard",
        extension=extension,
        component="admin",
        icon_name="pi-th-large",
        requires_group="collectivo.core.admin",
        parent="admin",
        order=80,
    )

    if settings.COLLECTIVO["example_data"]:
        DashboardTile.register(
            name="welcome_tile",
            label="Welcome to your platform!",
            extension=extension,
            source="db",
            order=0,
            content=(
                "Welcome {{ user.first_name }} {{ user.last_name }}. You can"
                " edit the content of this tile under the admin settings for"
                " the dashboard."
            ),
        )

        for i in range(1, 4, 1):
            button = DashboardTileButton.objects.register(
                name=f"example_button_{i}",
                label=f"Example Button {i}",
            )

            tile = DashboardTile.register(
                name=f"example_tile_{i}",
                label=f"Example Tile_{i}",
                extension=extension,
                source="db",
                content=(
                    "This is a custom tile. You can add as many as you want."
                ),
            )

            tile.buttons.set([button])

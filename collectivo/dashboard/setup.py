"""Setup function of the dashboard extension."""
from django.conf import settings

from collectivo.dashboard.apps import DashboardConfig
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.core.models import Permission, PermissionGroup
from .models import DashboardTile, DashboardTileButton


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    extension = Extension.objects.register(
        name=DashboardConfig.name,
        description=DashboardConfig.description,
        built_in=True,
    )

    MenuItem.objects.register(
        name="dashboard",
        label="Dashboard",
        extension=extension,
        route=extension.name + "/dashboard",
        icon_name="pi-home",
        parent="main",
        order=0,
    )

    # Set up permissions
    perms = {
        "view_dashboard_tiles": None,
        "edit_dashboard_tiles": None,
    }
    superuser = PermissionGroup.objects.get(name="superuser")
    for perm_name in perms:
        perms[perm_name] = perm = Permission.objects.register(
            name=perm_name,
            label=perm_name.replace("_", " ").capitalize(),
            description=f"Can {perm_name.replace('_', ' ')}",
            extension=extension,
        )
        superuser.permissions.add(perm)

    if settings.COLLECTIVO["example_data"]:
        DashboardTile.objects.register(
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

            tile = DashboardTile.objects.register(
                name=f"example_tile_{i}",
                label=f"Example Tile_{i}",
                extension=extension,
                source="db",
                content=(
                    "This is a custom tile. You can add as many as you want."
                ),
            )

            tile.buttons.set([button])

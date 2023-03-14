"""Setup function for the shifts extension."""
from collectivo.dashboard.models import DashboardTile
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.version import __version__

from .apps import ShiftsConfig


# TODO: Add required groups
def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    extension = Extension.register(
        name=ShiftsConfig.name.split(".")[-1],
        description=ShiftsConfig.description,
        version=__version__,
    )

    MenuItem.register(
        name="shifts_user",
        label="Shifts",
        extension=extension,
        component="shifts_user",
        menu_name="main",
    )

    MenuItem.register(
        name="shifts_admin",
        label="Shifts Administration",
        extension=extension,
        component="shifts_admin",
        menu_name="admin",
    )

    DashboardTile.register(
        name="shifts_user_tile",
        label="Shifts",
        extension=extension,
        component_name="shifts_user_tile",
    )

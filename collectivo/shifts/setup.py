"""Setup function for the shifts extension."""
from collectivo.dashboard.models import DashboardTile
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem

from .apps import ShiftsConfig


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    extension = Extension.register(
        name=ShiftsConfig.name,
        description=ShiftsConfig.description,
        built_in=True,
    )

    MenuItem.register(
        name="shifts_user",
        label="Shifts",
        icon_name="pi-calendar",
        extension=extension,
        component="shifts_user",
        requires_group="collectivo.shifts.user",
        parent="main",
    )

    MenuItem.register(
        name="shifts_admin",
        label="Shift management",
        icon_name="pi-calendar",
        extension=extension,
        component="admin",
        requires_group="collectivo.core.admin",
        parent="admin",
        order=30,
    )

    DashboardTile.register(
        name="shifts_user_tile",
        label="Shifts",
        extension=extension,
        component="shifts_user_tile",
        requires_group="collectivo.shifts.user",
    )

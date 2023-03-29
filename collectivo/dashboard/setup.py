"""Setup function of the menus extension."""
from collectivo.dashboard.apps import DashboardConfig
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.version import __version__


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

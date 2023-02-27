"""Setup function of the menus extension."""
from collectivo.dashboard.apps import DashboardConfig
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.version import __version__


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    dashboard_extension = Extension.register(
        name=DashboardConfig.name.split(".")[-1],
        description=DashboardConfig.description,
        version=__version__,
    )

    MenuItem.register(
        name="dashboard",
        label="Dashboard",
        extension=dashboard_extension,
        component_name="dashboard",
        icon_name="pi-home",
        menu_name="main",
        order=0,
    )

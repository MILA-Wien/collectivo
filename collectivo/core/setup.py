"""Setup function of the core extension."""
from collectivo.core.apps import CoreConfig
from collectivo.extensions.models import Extension
from collectivo.menus.models import Menu, MenuItem
from collectivo.version import __version__


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    core_extension = Extension.register(
        name=CoreConfig.name.split(".")[-1],
        description=CoreConfig.description,
        version=__version__,
    )

    Menu.register(name="main", extension=core_extension)
    Menu.register(name="admin", extension=core_extension)

    MenuItem.register(
        name="logout",
        label="Log out",
        extension=core_extension,
        component_name="logout",
        icon_name="pi-sign-out",
        menu_name="main",
        order=99,
    )

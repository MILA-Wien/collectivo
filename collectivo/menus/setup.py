"""Setup function of the menus extension."""
from collectivo.extensions.models import Extension
from collectivo.menus.models import Menu
from collectivo.menus.apps import MenusConfig
from collectivo.version import __version__


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    extension = Extension.register(
        name=MenusConfig.name,
        description=MenusConfig.description,
        version=__version__,
    )

    Menu.register(name="main_menu", extension=extension)
    Menu.register(name="admin_menu", extension=extension)

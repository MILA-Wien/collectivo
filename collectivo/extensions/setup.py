"""Setup function for the users module."""
from collectivo.extensions.apps import ExtensionsConfig
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.version import __version__


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    extensions_extension = Extension.register(
        name=ExtensionsConfig.name.split(".")[-1],
        description=ExtensionsConfig.description,
        version=__version__,
    )

    MenuItem.register(
        name="extensions",
        label="Extensions",
        extension=extensions_extension,
        menu_name="admin",
        component_name="extensions-list",
    )

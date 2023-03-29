"""Setup function of the menus extension."""
from collectivo.extensions.models import Extension
from collectivo.menus.apps import MenusConfig
from collectivo.version import __version__


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    Extension.register(
        name=MenusConfig.name,
        description=MenusConfig.description,
        version=__version__,
    )

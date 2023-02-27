"""Setup function for the users extension."""
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem
from collectivo.users.apps import UsersConfig
from collectivo.version import __version__


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    Extension.register(
        name=UsersConfig.name.split(".")[-1],
        description=UsersConfig.description,
        version=__version__,
    )

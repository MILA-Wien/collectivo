"""Setup function for the users extension."""
from collectivo.extensions.models import Extension
from collectivo.menus.models import Menu, MenuItem
from collectivo.users.models import Role
from collectivo.users.apps import UsersConfig
from collectivo.version import __version__


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    extension = Extension.register(
        name=UsersConfig.name,
        description=UsersConfig.description,
        version=__version__,
    )

    item = MenuItem.register(
        name="logout",
        label="Log out",
        extension=extension,
        action="component",
        component_name="logout",
        order=99,
    )
    item.add_to_menu("main")

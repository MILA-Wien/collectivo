"""Setup function of the core extension."""
from collectivo.extensions.models import Extension
from collectivo.users.models import Role
from collectivo.menus.models import Menu
from collectivo.core.apps import CoreConfig
from collectivo.version import __version__


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    core_extension = Extension.register(
        name=CoreConfig.name,
        description=CoreConfig.description,
        version=__version__,
    )

    Role.objects.get_or_create(name="superuser")

    Menu.register(name="main", extension=core_extension)
    Menu.register(name="admin", extension=core_extension)

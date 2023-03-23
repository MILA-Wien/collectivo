"""Setup function of the core extension."""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from collectivo.core.apps import CoreConfig
from collectivo.extensions.models import Extension
from collectivo.menus.models import Menu, MenuItem
from collectivo.version import __version__

User = get_user_model()

TEST_USERS = ["superuser", "user_not_member", "user_not_verified"] + [
    f"member_{str(i).zfill(2)}" for i in range(1, 4)
]


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    extension = Extension.register(
        name=CoreConfig.name.split(".")[-1],
        description=CoreConfig.description,
        version=__version__,
    )

    superuser = Group.objects.get_or_create(
        name="collectivo.core.admin",
    )[0]

    Menu.register(name="main", extension=extension)
    Menu.register(name="admin", extension=extension)

    MenuItem.register(
        name="users",
        label="Accounts",
        extension=extension,
        parent="admin",
        component="users",
        icon_name="pi-key",
        requires_group="collectivo.core.admin",
        order=80,
    )

    MenuItem.register(
        name="settings",
        label="Settings",
        extension=extension,
        parent="admin",
        component="settings",
        icon_name="pi-cog",
        requires_group="collectivo.core.admin",
        order=100,
    )

    MenuItem.register(
        name="logout",
        label="Log out",
        extension=extension,
        component="logout",
        icon_name="pi-sign-out",
        parent="main",
        order=99,
    )

    if settings.CREATE_TEST_DATA is True:
        for first_name in TEST_USERS:
            email = f"test_{first_name}@example.com"
            user = User.objects.get_or_create(
                username=email,
                email=email,
                first_name=first_name,
                last_name="Example",
            )[0]

            # Give user permissions
            if first_name == "superuser":
                user.groups.add(superuser)

"""Setup function of the core extension."""

import logging
import os

from django.conf import settings
from django.contrib.auth import get_user_model

from collectivo.core.apps import CoreConfig
from collectivo.core.models import Permission, PermissionGroup
from collectivo.extensions.models import Extension
from collectivo.menus.models import Menu, MenuItem
from collectivo.utils.dev import DEV_USERS
from collectivo.version import __version__

from .models import CoreSettings

User = get_user_model()
logger = logging.getLogger(__name__)


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    logger.info(f"Starting Collectivo v{__version__}")

    extension = Extension.objects.register(
        name=CoreConfig.name, description=CoreConfig.description, built_in=True
    )

    # Superuser permissions
    superuser = PermissionGroup.objects.register(
        name="superuser",
        label="Superuser",
        description="Admin access to all possible actions.",
        extension=extension,
    )
    coreadmin = Permission.objects.register(
        name="admin",
        label="Admin",
        description="Admin access to all possible actions.",
        extension=extension,
    )
    superuser.permissions.add(coreadmin)

    # Extension permissions
    perm_names = [
        "view_users",
        "edit_users",
        "view_groups",
        "edit_groups",
        "view_settings",
        "edit_settings",
    ]
    for perm_name in perm_names:
        perm = Permission.objects.register(
            name=perm_name,
            label=perm_name.replace("_", " ").capitalize(),
            description=f"Can {perm_name.replace('_', ' ')}",
            extension=extension,
        )
        superuser.permissions.add(perm)

    # User menu
    Menu.objects.register(name="main", extension=extension)
    MenuItem.objects.register(
        name="profile",
        label="Profile",
        extension=extension,
        route=extension.name + "/profile",
        icon_name="pi-user",
        parent="main",
    )
    MenuItem.objects.register(
        name="logout",
        label="Log out",
        extension=extension,
        route=extension.name + "/logout",
        icon_name="pi-sign-out",
        parent="main",
        order=99,
    )

    # Create admin menu
    Menu.objects.register(name="admin", extension=extension)
    MenuItem.objects.register(
        name="users",
        label="Users",
        extension=extension,
        parent="admin",
        route=extension.name + "/users",
        icon_name="pi-users",
        requires_perm=("view_users", "core"),
        order=00,
    )
    MenuItem.objects.register(
        name="settings",
        label="Settings",
        extension=extension,
        parent="admin",
        route=extension.name + "/settings",
        icon_name="pi-cog",
        requires_perm=("view_settings", "core"),
        order=100,
    )

    # Get admin user from env vars
    admin_user = os.environ.get("ADMIN_USER", None)
    admin_pass = os.environ.get("ADMIN_PASS", None)
    if admin_user and admin_pass:
        try:
            admin = User.objects.get(username=admin_user)
        except User.DoesNotExist:
            admin = User.objects.create(email=admin_user)
            admin.username = admin_user
            admin.first_name = admin_user
            admin.last_name = admin_user
            admin.save()
            admin.permission_groups.add(superuser)
            logger.info(f"Created admin user {admin_user}")

    if settings.COLLECTIVO["example_data"] is True:
        CoreSettings.object()  # This initializes the default settings

        for first_name in DEV_USERS:
            email = f"test_{first_name}@example.com"
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User.objects.create(email=email)
            user.username = email
            user.first_name = first_name[0].upper() + first_name[1:]
            user.last_name = "Example"
            user.save()

            # Give user permissions
            if first_name == "superuser":
                user.permission_groups.add(superuser)

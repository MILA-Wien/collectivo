"""Setup function for the shifts extension."""
from django.conf import settings

from collectivo.core.models import Permission, PermissionGroup
from collectivo.dashboard.models import DashboardTile
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem

from .apps import ShiftsConfig


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    extension = Extension.objects.register(
        name=ShiftsConfig.name,
        description=ShiftsConfig.description,
        built_in=True,
    )

    permissions = {}
    for p in ["use_shifts", "view_shifts", "edit_shifts"]:
        permissions[p] = Permission.objects.register(
            name=p,
            label=p.replace("_", " ").capitalize(),
            extension=extension,
        )

    MenuItem.objects.register(
        name="shifts_user",
        label="Shifts",
        icon_name="pi-calendar",
        extension=extension,
        route=extension.name + "/shifts_user",
        requires_perm=("use_shifts", "shifts"),
        parent="main",
    )

    MenuItem.objects.register(
        name="shifts_admin",
        label="Shift management",
        icon_name="pi-calendar",
        extension=extension,
        route=extension.name + "/admin",
        requires_perm=("view_shifts", "shifts"),
        parent="admin",
        order=30,
    )

    DashboardTile.objects.register(
        name="shifts_user_tile",
        label="Shifts",
        extension=extension,
        source="component",
        route=extension.name + "/shifts_user_tile",
        requires_perm=("use_shifts", "shifts"),
    )

    # Add shift admin permissions to superusers
    core = Extension.objects.get(name="core")
    superusers = PermissionGroup.objects.get(
        name="superuser",
        extension=core,
    )
    superusers.permissions.add(
        permissions["view_shifts"], permissions["edit_shifts"]
    )

    if settings.COLLECTIVO["example_data"] is True:
        all_users = PermissionGroup.objects.get(
            name="all_users",
            extension=core,
        )
        all_users.permissions.add(permissions["use_shifts"])

"""Setup function for the shifts extension."""
from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model

from collectivo.core.models import Permission, PermissionGroup
from collectivo.dashboard.models import DashboardTile
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem

from .apps import ShiftsConfig
from .models import Shift, ShiftProfile

User = get_user_model()


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

    # Create missing shift profiles
    users = User.objects.filter(shift_profile__isnull=True)
    for user in users:
        ShiftProfile.objects.create(user=user)

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

        for day in ["MO", "TU", "WE", "TH", "FR"]:
            for week in ["A", "B", "C", "D"]:
                for time in [("10:00", "13:00"), ("13:00", "16:00")]:
                    shift = Shift.objects.register(
                        name=f"Example {week} {day}",
                        description="This is an example shift.",
                        repeat="abcd",
                        abcd_week=week,
                        abcd_day=day,
                        starting_time=time[0],
                        ending_time=time[1],
                        required_users=2,
                    )

        # Non-repeating shifts
        shift = Shift.objects.register(
            name="Example shift (one-time)",
            description="This is an example shift that does not repeat.",
            repeat="none",
            date=date.today(),
            starting_time=time[0],
            ending_time=time[1],
            required_users=2,
        )

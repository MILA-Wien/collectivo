"""Setup function of the payments extension."""
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem

from .apps import PaymentsConfig


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    extension = Extension.objects.register(
        name=PaymentsConfig.name,
        description=PaymentsConfig.description,
        built_in=True,
    )

    MenuItem.objects.register(
        name="payments_admin",
        label="Payments",
        extension=extension,
        route=extension.name + "/admin",
        icon_name="pi-money-bill",
        requires_perm=("admin", "core"),
        parent="admin",
        order=20,
    )

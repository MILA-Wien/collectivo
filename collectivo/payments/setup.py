"""Setup function of the payments extension."""
from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem

from .apps import PaymentsConfig


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    extension = Extension.register(
        name=PaymentsConfig.name,
        description=PaymentsConfig.description,
        built_in=True,
    )

    MenuItem.register(
        name="payments_admin",
        label="Payments",
        extension=extension,
        component="admin",
        icon_name="pi-money-bill",
        requires_group="collectivo.core.admin",
        parent="admin",
        order=20,
    )

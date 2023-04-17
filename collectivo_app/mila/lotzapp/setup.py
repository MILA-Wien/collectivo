"""Setup function of the mila lotzapp extension."""
from collectivo.extensions.models import Extension


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    Extension.register(
        name="mila_lotzapp",
        label="MILA Lotzapp",
        description="Integration with the lotzapp ERP system.",
        version="1.0.0",
    )

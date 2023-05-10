"""Setup function of the mila lotzapp extension."""
from collectivo.extensions.models import Extension
from .models import LotzappSettings
import os


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    Extension.register(
        name="mila_lotzapp",
        label="MILA Lotzapp",
        description="Integration with the lotzapp ERP system.",
        version="1.0.0",
    )

    settings = LotzappSettings.object()
    settings.lotzapp_url = os.environ.get("LOTZAPP_URL", "")
    settings.lotzapp_user = os.environ.get("LOTZAPP_USER", "")
    settings.lotzapp_pass = os.environ.get("LOTZAPP_PASS", "")
    settings.save()

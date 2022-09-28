"""Manager for installed extensions."""
from django.apps import apps
from importlib import import_module
from django.utils.module_loading import module_has_submodule


def get_app_modules():
    """
    Return iterator over installed apps.

    Returns tuples of (app_name, module).
    """
    for app in apps.get_app_configs():
        yield app.name, app.module


def get_app_submodules(submodule_name):
    """
    Return iterator over apps that contain the specified submodule.

    Returns tuples of (app_name, submodule).
    """
    for name, module in get_app_modules():
        if module_has_submodule(module, submodule_name):
            yield name, import_module("%s.%s" % (name, submodule_name))


class ExtensionManager:
    """Manager for installed extensions."""

    def __init__(self):
        """Load extensions."""
        self.extensions = {
            name: extension for name, extension
            in get_app_submodules("collectivo")
        }


# This object is a global instance of ExtensionManager
# that can be imported and used by other modules.
extension_manager = ExtensionManager()

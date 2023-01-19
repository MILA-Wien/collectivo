"""Utility functions of the extensions module."""
import logging
from collectivo.extensions.views import ExtensionViewSet
from collectivo.utils import request
from rest_framework.response import Response


logger = logging.getLogger(__name__)


def register_extension(name: str, **kwargs) -> Response:
    """Register an internal extension."""
    kwargs['name'] = name
    request(ExtensionViewSet, 'destroy', kwargs, pk=name)
    response = request(ExtensionViewSet, 'create', kwargs, pk=name)
    if response.status_code != 201:
        logger.debug(
            f"Could not register extension '{name}': {response.content}")
    return response

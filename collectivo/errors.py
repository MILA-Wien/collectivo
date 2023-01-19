"""Error classes of the collectivo package."""
from rest_framework.exceptions import APIException


class CollectivoError(Exception):
    """Custom error type for collectivo."""

    pass


class BadRequest(APIException):
    """Custom error for bad requests."""

    status_code = 400

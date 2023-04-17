"""Exceptions for collectivo."""
from rest_framework.exceptions import APIException


class CollectivoAPIException(APIException):
    """Base exception for collectivo."""

    pass


class ExtensionNotInstalled(CollectivoAPIException):
    """Exception for when an extension is not installed."""

    pass

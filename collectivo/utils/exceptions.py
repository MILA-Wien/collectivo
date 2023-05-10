"""Exceptions for collectivo."""
from rest_framework.exceptions import APIException


class APIException(APIException):
    """Base exception for collectivo."""

    pass


class ImproperlyConfigured(APIException):
    """Exception for when a setting is not configured correctly."""

    status_code = 500


class ExtensionNotInstalled(APIException):
    """Exception for when an extension is not installed."""

    status_code = 500

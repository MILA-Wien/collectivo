"""Core permissions of collectivo."""
# Thanks to https://stackoverflow.com/a/19429199/14396787
import logging

from rest_framework import permissions
from rest_framework.permissions import BasePermission

from collectivo.core.models import Permission

logger = logging.getLogger(__name__)


def is_superuser(user):
    """Check if user is superuser."""
    try:
        return user.permission_groups.filter(
            name="superuser", extension__name="core"
        ).exists()
    except AttributeError:
        return None


def has_permission(user, perm_name: str, ext_name: str = None) -> bool | None:
    """Check if user has permission."""
    try:
        return Permission.objects.filter(
            name=perm_name,
            extension__name=ext_name,
            groups__in=user.permission_groups.all(),
        ).exists()
    except Permission.DoesNotExist:
        return None
    except AttributeError:
        return None


class IsAuthenticated(BasePermission):
    """Allow access only to authenticated users."""

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated


class IsSuperuser(BasePermission):
    """Allow access only to superusers."""

    def has_permission(self, request, view):
        """Check if user is superuser."""
        return is_superuser(request.user)


class ReadOrIsSuperuser(BasePermission):
    """Ensure user is authenticated to read or is superuser."""

    def has_permission(self, request, view):
        """Check if permission is given."""
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return is_superuser(request.user)


class HasPerm(BasePermission):
    """
    Ensure user has required permissions.

    Required permissions are taken from the view's `required_perms` attribute,
    which should be a dictionary mapping methods to required permissions.
    The method "ALL" can be used to specify a permission for all methods.
    Permissions must be a list of tuples of the permission and extension name.
    If multple permissions are given, the user must have only one of them.

    Example:
    ```
    class MyView(APIView):
        required_perms = {
            "GET": [("my_permission", "my_extension")],
            "POST": [("my_permission", "my_extension")],
            "PUT": [("my_permission", "my_extension")],
            "PATCH": [("my_permission", "my_extension")],
            "DELETE": [("my_permission", "my_extension")],
            "ALL": [("my_permission", "my_extension")],
        }
    """

    def has_permission(self, request, view):
        """Check if user has required permissions."""
        # Get a mapping of methods -> required group.
        required_perms = getattr(view, "required_perms", [])

        if not isinstance(required_perms, dict):
            logger.warn("Invalid permission in serializer.")
            return False

        methods = required_perms.keys()
        required_perms_for_method = []

        if request.method in methods:
            required_perms_for_method += required_perms[request.method]

        if "ALL" in methods:
            required_perms_for_method += required_perms["ALL"]

        # Return True if the user has all the required groups or is superuser.
        return any(
            {
                has_permission(request.user, perm_name, ext_name)
                if perm_name != "__all__"
                else True
                for perm_name, ext_name in required_perms_for_method
            }
        ) or is_superuser(request.user)


class ReadOrHasGroup(HasPerm):
    """Ensure user is authenticated to read or is in required group."""

    def has_permission(self, request, view):
        """Check if permission is given."""
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return super().has_permission(request, view)

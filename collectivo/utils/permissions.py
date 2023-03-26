"""Core permissions of collectivo."""
# Thanks to https://stackoverflow.com/a/19429199/14396787
from django.contrib.auth.models import Group
from rest_framework import permissions
from rest_framework.permissions import BasePermission


def is_in_group(user, group_name: str) -> bool | None:
    """Check if user is in group."""
    try:
        return (
            Group.objects.get(name=group_name)
            .user_set.filter(id=user.id)
            .exists()
        )
    except Group.DoesNotExist:
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
        return is_in_group(request.user, "collectivo.core.admin")


class ReadOrIsSuperuser(BasePermission):
    """Ensure user is authenticated to read or is superuser."""

    def has_permission(self, request, view):
        """Check if permission is given."""
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return is_in_group(request.user, "collectivo.core.admin")


class HasGroup(BasePermission):
    """Ensure user is in required groups."""

    def has_permission(self, request, view):
        """Check if user is in required groups."""
        # Get a mapping of methods -> required group.
        required_groups = getattr(view, "required_groups", [])

        if isinstance(required_groups, dict):
            # Determine the required groups for this particular request method.
            required_groups = required_groups.get(request.method, [])

        # Return True if the user has all the required groups or is superuser.
        return all(
            [
                is_in_group(request.user, group_name)
                if group_name != "__all__"
                else True
                for group_name in required_groups
            ]
        ) or is_in_group(request.user, "collectivo.core.admin")


class ReadOrHasGroup(HasGroup):
    """Ensure user is authenticated to read or is in required group."""

    def has_permission(self, request, view):
        """Check if permission is given."""
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return super().has_permission(request, view)

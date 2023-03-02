"""Core permissions of collectivo."""
from rest_framework.permissions import BasePermission


class IsSuperuser(BasePermission):
    """Allow access only to superusers."""

    def has_permission(self, request, view):
        """Check if user is superuser."""
        return request.user.has_perm("collectivo.core.admin")

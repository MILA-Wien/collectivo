"""Permissions of the members extension."""
from rest_framework import permissions


class IsPaymentsAdmin(permissions.BasePermission):
    """Permission to check if user has admin access to this extension."""

    def has_permission(self, request, view):
        """Check if the required permission is among user roles."""
        return request.userinfo.has_role_or_is_superuser("payments_admin")

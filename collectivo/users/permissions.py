"""Permissions of the keycloak module to be used in DRF views."""
from rest_framework import permissions


class IsAuthenticated(permissions.BasePermission):
    """Permission to check if user is authenticated."""

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user.is_authenticated


class IsSuperuser(permissions.BasePermission):
    """Permission to check if user has the role 'superuser'."""

    def has_permission(self, request, view):
        """Check if the required permission is among user roles."""
        return request.auth_user.is_superuser

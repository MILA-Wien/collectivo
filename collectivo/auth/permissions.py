"""Permissions of the keycloak module to be used in DRF views."""
from rest_framework import permissions


class IsAuthenticated(permissions.BasePermission):
    """Permission to check if user is authenticated."""

    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.userinfo.is_authenticated


class IsSuperuser(permissions.BasePermission):
    """Permission to check if user has the role 'superuser'."""

    def has_permission(self, request, view):
        """Check if the required permission is among user roles."""
        return request.userinfo.has_role_or_is_superuser()


class IsSelf(permissions.BasePermission):
    """Permission to check if the object has the user's id."""

    def has_object_permission(self, request, view, obj):
        """Check if the object has the user's id."""
        if hasattr(obj, 'user_id'):
            return request.userinfo.user_id == obj.user_id
        else:
            return False

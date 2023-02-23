"""Views of the user experience module."""
from django.db.models import Q
from rest_framework import viewsets, mixins
from . import models, serializers
from collectivo.users.permissions import IsSuperuser, IsAuthenticated
import logging
from collectivo.extensions.models import Extension
from collectivo.menus.models import Menu


logger = logging.getLogger(__name__)


class MenuViewSet(viewsets.ModelViewSet):
    """Manage menus.

    List view requires authentication.
    All other views require the role 'superuser'.

    Attributes:
    - menu_id (CharField): A unique name to identify the menu.
    - extension (ForeignKey of Extension):
      The extension that the menu belongs to.
    """

    queryset = models.Menu.objects.all()

    def get_permissions(self):
        """Set permissions for this viewset."""
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]
        return [IsSuperuser()]

    def get_serializer_class(self):
        """Set name to read-only except for create."""
        if self.request.method == "POST":
            return serializers.MenuCreateSerializer
        return serializers.MenuSerializer

    def get_queryset(self):
        """Show only menus where user has required roles."""
        extension = self.request.query_params.get("extension", None)
        menu = self.request.query_params.get("menu", None)
        queryset = models.Menu.objects.filter(
            name=menu,
            extension=Extension.objects.get(name=extension),
        )
        return queryset


class MenuItemViewSet(viewsets.ModelViewSet):
    """Manage menu-items.

    List view requires authentication.
    Only items where the user has the required roles are shown.

    All other views require the role 'superuser'.
    """

    queryset = models.MenuItem.objects.all()

    def get_permissions(self):
        """Set permissions for this viewset."""
        if self.action == "list":
            return [IsAuthenticated()]
        return [IsSuperuser()]

    def get_serializer_class(self):
        """Set item_id to read-only except for create."""
        if self.request.method == "POST":
            return serializers.MenuItemCreateSerializer
        return serializers.MenuItemSerializer

    def get_queryset(self):
        """Show only items where user has required roles."""
        user_roles = self.request.auth_user.roles.all()
        queryset = models.MenuItem.objects.filter(
            Q(required_role__in=user_roles) | Q(required_role=None)
        ).order_by("order")
        return queryset

"""Views of the user experience module."""
import logging

from django.db.models import Q
from rest_framework import mixins, viewsets

from collectivo.extensions.models import Extension
from collectivo.menus.models import Menu
from collectivo.users.permissions import IsAuthenticated, IsSuperuser

from . import models, serializers

logger = logging.getLogger(__name__)


class MenuViewSet(viewsets.ModelViewSet):
    """Manage menus.

    GET requires authentication. All other views require the role 'superuser'.

    Menus can be filtered with the attributes 'menu' and 'extension'.
    The main menu can filtered with `?extension=core&menu=main`.
    """

    queryset = models.Menu.objects.all()
    serializer_class = serializers.MenuSerializer

    def get_permissions(self):
        """Set permissions for this viewset."""
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsSuperuser()]

    def get_queryset(self):
        """Allow filtering after extension and menu name."""
        extension = self.request.query_params.get("extension", None)
        menu_name = self.request.query_params.get("menu", None)
        queryset = models.Menu.objects.all()
        if extension:
            queryset = queryset.filter(
                extension=Extension.objects.get(name=extension)
            )
        if menu_name:
            queryset = queryset.filter(name=menu_name)

        return queryset


class MenuItemViewSet(viewsets.ModelViewSet):
    """Manage menu-items.

    List view requires authentication.
    Only items where the user has the required roles are shown.

    All other views require the role 'superuser'.
    """

    queryset = models.MenuItem.objects.all()
    serializer_class = serializers.MenuItemSerializer

    def get_permissions(self):
        """Set permissions for this viewset."""
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsSuperuser()]

    def get_queryset(self):
        """Show only items where user has required roles."""
        user_roles = self.request.auth_user.roles.all()
        queryset = models.MenuItem.objects.filter(
            Q(required_role__in=user_roles) | Q(required_role=None)
        ).order_by("order")
        return queryset

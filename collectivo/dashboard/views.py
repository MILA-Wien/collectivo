"""Views of the dashboard extension."""
from django.db.models import Q
from rest_framework import viewsets
from collectivo.auth.permissions import IsSuperuser, IsAuthenticated
from . import models, serializers


class DashboardTileViewSet(viewsets.ModelViewSet):
    """
    Manage dashboard tiles.

    List view requires authentication.
    All other views require the role 'superuser'.

    Dashboard tiles refer to webcomponents
    that will be displayed in the dashboard.

    Attributes:
    - tile_id (CharField):
      A unique name to identify the tile.
    - extension (ForeignKey of Extension):
      The extension that the menu belongs to.
    - component_name (str):
      Name of a registered component from the extensions' microfrontend.
      The URL path after performing the action will be
      '{base_url}/{extension}/{component name}'.
    - order (FloatField):
      Tiles will be sorted from lowest to highest order (default 1.0).
    - required_role (CharField, optional):
      If passed, only users with this role will see the tile.
    - blocked_role (CharField, optional):
      If passed, users with this role will not see the tile.
    """

    def get_queryset(self):
        """Show only items where user has required roles."""
        user_roles = self.request.userinfo.roles

        queryset = models.DashboardTile.objects.filter(
            Q(required_role__in=user_roles) |
            Q(required_role=None),
            ~Q(blocked_role__in=user_roles)
        )
        return queryset

    def get_permissions(self):
        """Set permissions for this viewset."""
        if self.action == 'list':
            return [IsAuthenticated()]
        return [IsSuperuser()]

    def get_serializer_class(self):
        """Set name to read-only except for create."""
        if self.request.method == 'POST':
            return serializers.DashboardTileCreateSerializer
        return serializers.DashboardTileSerializer

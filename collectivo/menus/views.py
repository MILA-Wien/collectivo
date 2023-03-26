"""Views of the menus extension."""
import logging

from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from collectivo.utils.permissions import IsSuperuser

from . import models, serializers

logger = logging.getLogger(__name__)


class MenuViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """Manage menus.

    Menus are not retrieved by ID, but by extension and menu name.
    Requires authentication to read (GET), and the role 'superuser' to write.
    """

    queryset = models.Menu.objects.all()
    serializer_class = serializers.MenuSerializer

    def get_permissions(self):
        """Set permissions for this viewset."""
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsSuperuser()]

    @action(
        methods=["GET"],
        detail=False,
        url_path=r"(?P<extension>\w+)/(?P<menu>\w+)",
        url_name="detail",
    )
    def retrieve_with_params(self, request: Request, extension, menu):
        """Get menu based on extension and menu name."""
        queryset = self.get_queryset()
        menu = queryset.get(extension__name=extension, name=menu)
        serializer = self.get_serializer(menu)
        return Response(serializer.data)


class MenuItemViewSet(viewsets.ModelViewSet):
    """Manage menu-items. Requires the role 'superuser'."""

    queryset = models.MenuItem.objects.all()
    serializer_class = serializers.MenuItemSerializer
    permission_classes = [IsSuperuser]

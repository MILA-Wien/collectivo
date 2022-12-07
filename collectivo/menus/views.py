"""Views of the user experience module."""
from django.db.models import Q
from rest_framework import viewsets
from . import models, serializers
from collectivo.auth.permissions import IsSuperuser, IsAuthenticated
import logging


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
        if self.action == 'list':
            return [IsAuthenticated()]
        return [IsSuperuser()]

    def get_serializer_class(self):
        """Set name to read-only except for create."""
        if self.request.method == 'POST':
            return serializers.MenuCreateSerializer
        return serializers.MenuSerializer


class MenuItemViewSet(viewsets.ModelViewSet):
    """Manage menu-items.

    List view requires authentication.
    Only items where the user has the required roles are shown.

    All other views require the role 'superuser'.

    Attributes:
    - item_id (CharField):
      A unique name to identify the item.
      Can only be written to with POST.
    - menu_id (ForeignKey of Menu):
      The menu that the item belongs to.
    - label (CharField):
      Text to be displayed in the menu item.
    - extension (ForeignKey of Extension):
      The extension that the item belongs to.
    - action (CharField, optional):
      Action to be performed when the item is clicked.
      If none is passed, no action will be performed.
      <br/>Options:
        - 'component': Load a webcomponent.
        - 'link': Open a link.
    - action_target (str, optional):
      The location where the action will be performed.
      Required if an action is passed.
      <br/>Options:
        - 'main': Main application window (default).
        - 'blank': A new browser tab.
    - component_name (str, optional):
      Name of a registered component from the extensions' microfrontend.
      The URL path after performing the action will be
      '{base_url}/{extension}/{component name}'.
      Required if action is 'component'.
    - link_source (URLField, optional):
      URL to be opened. Required if action is 'link'.
    - order (FloatField, optional):
      Items will be sorted from lowest to highest order (default 1.0).
    - parent_item (ForeignKey of MenuItem, optional):
      A menu item that this item will be subordinate to.
    - style (CharField, optional):
      Pre-set style options for the menu item.
      <br/>Options:
        - 'normal': The standard style (default).
    - required_role (CharField, optional):
      If passed, only users with this role will see the menu item.
    - icon_name_prime (CharField, optional):
      Name of a prime icon to be used by primevue frontend applications.
      See: https://github.com/primefaces/primeicons
    - icon_path (URLField, optional):
      Path to an icon image.
    """

    def get_permissions(self):
        """Set permissions for this viewset."""
        if self.action == 'list':
            return [IsAuthenticated()]
        return [IsSuperuser()]

    def get_serializer_class(self):
        """Set item_id to read-only except for create."""
        if self.request.method == 'POST':
            return serializers.MenuItemCreateSerializer
        return serializers.MenuItemSerializer

    def get_queryset(self):
        """Show only items where user has required roles."""
        user_roles = self.request.userinfo.roles
        queryset = models.MenuItem.objects.filter(
            Q(required_role__in=user_roles) |
            Q(required_role=None)
        ).order_by('order')
        return queryset

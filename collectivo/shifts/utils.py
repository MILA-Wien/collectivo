"""Utility functions of the user experience module."""
from collectivo.menus import views
from collectivo.utils import register_viewset


def register_menu(**payload):
    """Register a menu."""
    pk = payload['menu_id']
    return register_viewset(views.MenuViewSet, pk, payload=payload)


def register_menuitem(**payload):
    """Register a menu item."""
    pk = payload['item_id']
    return register_viewset(views.MenuItemViewSet, pk, payload=payload)

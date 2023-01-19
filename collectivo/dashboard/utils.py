"""Utility functions of the dashboard module."""
from collectivo.utils import register_viewset
from .views import DashboardTileViewSet


def register_tile(**payload):
    """Register a dashboard tile."""
    pk = payload['tile_id']
    return register_viewset(DashboardTileViewSet, pk, payload=payload)

"""Routers of the collectivo package."""
from rest_framework.routers import Route, SimpleRouter, DynamicRoute


class DirectDetailRouter(SimpleRouter):
    """A DRF router for detail views that don't need a primary key."""

    routes = [
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'post': 'create',
                'patch': 'partial_update',
                'put': 'update'
            },
            name='{basename}',
            detail=False,
            initkwargs={'suffix': 'Instance'}
        ),
        DynamicRoute(
            url=r'^{prefix}/{url_path}{trailing_slash}$',
            name='{basename}-{url_name}',
            detail=False,
            initkwargs={}
        ),
    ]

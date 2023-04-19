"""Views of the dashboard extension."""
from django.db.models import Q
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from collectivo.utils.mixins import HistoryMixin, SchemaMixin
from collectivo.utils.permissions import IsAuthenticated, IsSuperuser

from .models import DashboardTile, DashboardTileButton
from .serializers import (
    TileButtonSerializer,
    TileDisplaySerializer,
    TileSerializer,
)


class DashboardTileViewSet(HistoryMixin, SchemaMixin, viewsets.ModelViewSet):
    """
    Manage dashboard tiles.

    Requires authentication to read, otherwise superuser.

    Dashboard tiles refer to webcomponents
    that will be displayed in the dashboard.
    Only tiles where the user has the required group are shown.
    """

    queryset = DashboardTile.objects.all()
    serializer_class = TileSerializer
    permission_classes = [IsSuperuser]

    @extend_schema(responses={200: OpenApiResponse()})
    @action(
        url_path="self",
        url_name="self",
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def display_for_user(self, request):
        """Return filtered tiles for authenticated user."""
        queryset = DashboardTile.objects.filter(
            Q(active=True)
            & (
                Q(requires_group=None)
                | Q(requires_group__in=request.user.groups.all())
            )
        )
        serializer_class = TileDisplaySerializer

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data)


class DashboardTileButtonViewSet(
    HistoryMixin, SchemaMixin, viewsets.ModelViewSet
):
    """Manage dashboard tile buttons."""

    queryset = DashboardTileButton.objects.all()
    serializer_class = TileButtonSerializer
    permission_classes = [IsSuperuser]

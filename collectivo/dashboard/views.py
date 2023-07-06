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

        groups = request.user.permission_groups.all()

        queryset = (
            DashboardTile.objects.filter(
                Q(active=True),
                (
                    Q(requires_not_perm=None)
                    | ~Q(requires_not_perm__groups__in=groups)
                ),
                (Q(requires_perm=None) | Q(requires_perm__groups__in=groups)),
            )
            .order_by("order")
            .distinct()
        )

        serializer_class = TileDisplaySerializer

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializer_class(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = serializer_class(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)


class DashboardTileButtonViewSet(
    HistoryMixin, SchemaMixin, viewsets.ModelViewSet
):
    """Manage dashboard tile buttons."""

    queryset = DashboardTileButton.objects.all()
    serializer_class = TileButtonSerializer
    permission_classes = [IsSuperuser]

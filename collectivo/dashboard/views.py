"""Views of the dashboard extension."""
from django.db.models import Q
from rest_framework import viewsets

from collectivo.utils.permissions import ReadOrIsSuperuser

from . import models, serializers


class DashboardTileViewSet(viewsets.ModelViewSet):
    """
    Manage dashboard tiles.

    Requires authentication to read, otherwise superuser.

    Dashboard tiles refer to webcomponents
    that will be displayed in the dashboard.
    Only tiles where the user has the required group are shown.
    """

    serializer_class = serializers.DashboardTileSerializer
    permission_classes = [ReadOrIsSuperuser]

    def get_queryset(self):
        """Show only items where user has required group."""
        queryset = models.DashboardTile.objects.filter(
            Q(requires_group=None)
            | Q(requires_group__in=self.request.user.groups.all())
        )
        return queryset

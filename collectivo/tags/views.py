"""Views of the tags extension."""
import logging

from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError

from collectivo.utils.filters import get_filterset, get_ordering_fields
from collectivo.utils.mixins import HistoryMixin, SchemaMixin
from collectivo.utils.permissions import HasPerm, IsSuperuser

from . import models, serializers

logger = logging.getLogger(__name__)

User = get_user_model()


class TagProfileViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage tags assigned to users."""

    permission_classes = [HasPerm]
    required_perms = {
        "GET": [("view_users", "core")],
        "ALL": [("edit_users", "core")],
    }
    queryset = User.objects.all()
    serializer_class = serializers.TagProfileSerializer
    permission_classes = [IsSuperuser]
    filterset_class = get_filterset(serializers.TagProfileSerializer)
    ordering_fields = get_ordering_fields(serializers.TagProfileSerializer)


class TagViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage tags."""

    permission_classes = [HasPerm]
    required_perms = {
        "GET": [("view_users", "core")],
        "ALL": [("edit_users", "core")],
    }
    serializer_class = serializers.TagSerializer
    queryset = models.Tag.objects.all()
    filterset_class = get_filterset(serializers.TagSerializer)
    ordering_fields = get_ordering_fields(serializers.TagSerializer)

    def perform_destroy(self, instance):
        """Prevent deletion if assigned to users."""

        if instance.users.all().exists():
            raise ValidationError(
                "Cannot delete a tag that is assigned to users."
            )
        return super().perform_destroy(instance)


class TagHistoryViewSet(
    SchemaMixin, HistoryMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """View history of a tag."""

    permission_classes = [HasPerm]
    required_perms = {
        "GET": [("view_users", "core")],
        "ALL": [("edit_users", "core")],
    }
    serializer_class = serializers.TagHistorySerializer
    queryset = models.Tag.history.model.objects.all()
    filterset_class = get_filterset(serializers.TagHistorySerializer)
    ordering_fields = get_ordering_fields(serializers.TagHistorySerializer)

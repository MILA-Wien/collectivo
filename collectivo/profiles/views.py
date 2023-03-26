"""Views of the profiles extension."""
from rest_framework import mixins, viewsets
from rest_framework.exceptions import ParseError

from collectivo.utils.filters import get_filterset, get_ordering_fields
from collectivo.utils.mixins import HistoryMixin, SchemaMixin
from collectivo.utils.permissions import HasGroup, IsAuthenticated

from . import serializers
from .models import UserProfile


class ProfileUserViewSet(
    SchemaMixin,
    HistoryMixin,
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    """ViewSet for users to manage their own profile."""

    queryset = UserProfile.objects.all()
    serializer_class = serializers.ProfileUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return member object of the currently authenticated user."""
        try:
            return self.queryset.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            raise ParseError("User has no profile.")


class ProfileAdminViewSet(
    SchemaMixin,
    HistoryMixin,
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
):
    """ViewSet for admins to manage user profiles."""

    queryset = UserProfile.objects.all()
    serializer_class = serializers.ProfileAdminSerializer
    permission_classes = [HasGroup]
    required_groups = ["collectivo.profiles.admin"]
    filterset_class = get_filterset(serializers.ProfileAdminSerializer)
    ordering_fields = get_ordering_fields(serializers.ProfileAdminSerializer)

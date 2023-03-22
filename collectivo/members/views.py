"""Views of the members extension."""
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from collectivo.core.permissions import HasGroup
from collectivo.utils.filters import get_filterset, get_ordering_fields
from collectivo.utils.history import HistoryMixin
from collectivo.utils.schema import SchemaMixin

from . import serializers
from .models import MemberProfile, Membership


class MemberRegisterViewSet(
    SchemaMixin, HistoryMixin, viewsets.GenericViewSet, mixins.CreateModelMixin
):
    """
    API for members to register themselves.

    Requires authentication.
    """

    queryset = MemberProfile.objects.all()
    serializer_class = serializers.MemberRegisterSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Create member with authenticated user."""
        extra_fields = {
            "user": self.request.user,
        }
        if "tags" in serializer.validated_data:
            extra_fields["tags"] = serializer.validated_data["tags"]
        serializer.save(**extra_fields)


class MemberProfileViewSet(
    SchemaMixin,
    HistoryMixin,
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    """
    API for members to manage themselves.

    Requires authentication and registration.
    """

    queryset = MemberProfile.objects.all()
    serializer_class = serializers.MemberProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return member object of the currently authenticated user."""
        try:
            return self.queryset.get(user=self.request.user)
        except MemberProfile.DoesNotExist:
            raise PermissionDenied("User is not registered as a member.")


class MembersViewSet(
    SchemaMixin,
    HistoryMixin,
    viewsets.ModelViewSet,
):
    """
    API for admins to manage members.

    Requires the role 'members_admin'.
    """

    queryset = MemberProfile.objects.all()
    serializer_class = serializers.MemberSerializer
    permission_classes = [HasGroup]
    required_groups = ["collectivo.members.admin"]
    filterset_class = get_filterset(serializers.MemberSerializer)
    ordering_fields = get_ordering_fields(serializers.MemberSerializer)


class MembershipViewSet(SchemaMixin, HistoryMixin, viewsets.ModelViewSet):
    """
    API for admins to manage memberships.

    Requires the group 'collectivo.members.admin'.
    """

    queryset = Membership.objects.all()
    serializer_class = serializers.MembershipSerializer
    permission_classes = [HasGroup]
    required_groups = ["collectivo.members.admin"]
    filterset_class = get_filterset(serializers.MembershipSerializer)
    ordering_fields = get_ordering_fields(serializers.MembershipSerializer)

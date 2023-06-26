"""Views of the memberships extension."""
from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from collectivo.utils.filters import get_filterset, get_ordering_fields
from collectivo.utils.mixins import BulkEditMixin, HistoryMixin, SchemaMixin
from collectivo.utils.permissions import HasPerm, IsAuthenticated

from . import serializers
from .models import Membership, MembershipStatus, MembershipType

User = get_user_model()


class MembershipAdminViewSet(SchemaMixin, BulkEditMixin, ModelViewSet):
    """ViewSet to manage memberships with a type and status."""

    queryset = Membership.objects.all()
    serializer_class = serializers.MembershipSerializer
    permission_classes = [HasPerm]
    required_perms = {
        "GET": [("view_memberships", "memberships")],
        "ALL": [("edit_memberships", "memberships")],
    }
    filterset_class = get_filterset(serializer_class)
    ordering_fields = get_ordering_fields(serializer_class)


class MembershipProfileViewSet(SchemaMixin, ModelViewSet):
    """Manage memberships assigned to users."""

    queryset = User.objects.all()
    serializer_class = serializers.MembershipProfileSerializer
    permission_classes = [HasPerm]
    required_perms = {
        "GET": [("view_memberships", "memberships")],
        "ALL": [("edit_memberships", "memberships")],
    }
    filterset_class = get_filterset(serializers.MembershipProfileSerializer)
    ordering_fields = get_ordering_fields(
        serializers.MembershipProfileSerializer
    )


class MembershipRegisterViewset(
    SchemaMixin, CreateModelMixin, RetrieveModelMixin, GenericViewSet
):
    """ViewSet to register new memberships with additional serializers."""

    queryset = MembershipType.objects.all()
    serializer_class = serializers.MembershipRegisterCombinedSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        """Retrieve the membership type with additional serializers."""
        instance = self.get_object()
        serializer = (
            serializers.MembershipRegisterCombinedSerializer.initialize(
                instance, request.user
            )
        )
        return Response(serializer.data)


class MembershipUserViewSet(
    SchemaMixin, ListModelMixin, UpdateModelMixin, GenericViewSet
):
    """ViewSet for users to see their own memberships."""

    queryset = Membership.objects.all()
    serializer_class = serializers.MembershipSelfSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = get_filterset(serializer_class)
    ordering_fields = get_ordering_fields(serializer_class)

    def get_queryset(self):
        """Return only the memberships of the current user."""
        return self.queryset.filter(user=self.request.user)


class MembershipTypeViewSet(SchemaMixin, ModelViewSet):
    """ViewSet to manage membership types (e.g. member of a collective)."""

    queryset = MembershipType.objects.all()
    serializer_class = serializers.MembershipTypeSerializer
    permission_classes = [HasPerm]
    required_perms = {
        "GET": [("view_memberships", "memberships")],
        "ALL": [("edit_settings", "memberships")],
    }
    filterset_class = get_filterset(serializer_class)
    ordering_fields = get_ordering_fields(serializer_class)


class MembershipStatusViewSet(SchemaMixin, ModelViewSet):
    """ViewSet to manage membership statuses (e.g. active or investing)."""

    queryset = MembershipStatus.objects.all()
    serializer_class = serializers.MembershipStatusSerializer
    permission_classes = [HasPerm]
    required_perms = {
        "GET": [("view_memberships", "memberships")],
        "ALL": [("edit_settings", "memberships")],
    }
    filterset_class = get_filterset(serializer_class)
    ordering_fields = get_ordering_fields(serializer_class)


class MembershipHistoryViewSet(
    SchemaMixin, HistoryMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """View history of a Membership."""

    permission_classes = [HasPerm]
    required_perms = {
        "GET": [("view_memberships", "memberships")],
        "ALL": [("edit_settings", "memberships")],
    }
    serializer_class = serializers.MembershipHistorySerializer
    queryset = Membership.history.model.objects.all()
    filterset_class = get_filterset(serializers.MembershipHistorySerializer)
    ordering_fields = get_ordering_fields(
        serializers.MembershipHistorySerializer
    )


class MembershipTypeHistoryViewSet(
    SchemaMixin, HistoryMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """View history of a Membership Type."""

    permission_classes = [HasPerm]
    required_perms = {
        "GET": [("view_memberships", "memberships")],
        "ALL": [("edit_settings", "memberships")],
    }
    serializer_class = serializers.MembershipTypeHistorySerializer
    queryset = MembershipType.history.model.objects.all()
    filterset_class = get_filterset(
        serializers.MembershipTypeHistorySerializer
    )
    ordering_fields = get_ordering_fields(
        serializers.MembershipTypeHistorySerializer
    )

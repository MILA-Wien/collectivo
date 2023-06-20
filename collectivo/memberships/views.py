"""Views of the memberships extension."""
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from collectivo.utils.filters import get_filterset, get_ordering_fields
from collectivo.utils.mixins import HistoryMixin, SchemaMixin
from collectivo.utils.permissions import HasPerm, IsAuthenticated

from . import serializers
from .models import Membership, MembershipStatus, MembershipType

User = get_user_model()


class MembershipAdminViewSet(SchemaMixin, HistoryMixin, ModelViewSet):
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

    @extend_schema(responses={200: OpenApiResponse()})
    @action(
        url_path="create_invoices",
        url_name="create_invoices",
        methods=["post"],
        detail=False,
    )
    def create_invoices(self, request, *args, **kwargs):
        """Create invoices for all memberships."""
        with transaction.atomic():
            for membership in self.get_queryset():
                membership.create_invoices()
        return Response({"message": "Invoices created."})


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


# logger = logging.getLogger(__name__)
# registration_serializers = settings.COLLECTIVO["extensions"][
#     "collectivo.memberships"
# ].get("registration_serializers", {})
# print("REGISTRATION SERIALIZERS", registration_serializers)
# if not isinstance(registration_serializers, list):
#     logger.warn("The 'registration_serializers' setting must be a list.")
#     registration_serializers = []


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

    # def retrieve(self, request, *args, **kwargs):
    #     type = self.get_object()
    #     payload = object()
    #     for item in registration_serializers:
    #         for method, serializer in item.items():
    #             serializer = import_string(serializer)
    #             setattr(payload, obj)
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)


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


class MembershipTypeViewSet(SchemaMixin, HistoryMixin, ModelViewSet):
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


class MembershipStatusViewSet(SchemaMixin, HistoryMixin, ModelViewSet):
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

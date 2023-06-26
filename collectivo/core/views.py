"""Views of the core extension."""
from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from collectivo.utils.filters import get_filterset, get_ordering_fields
from collectivo.utils.mixins import SchemaMixin
from collectivo.utils.permissions import (
    HasPerm,
    IsSuperuser,
    ReadOrIsSuperuser,
)
from collectivo.utils.viewsets import (
    ExtensionModelViewSet,
    HistoryViewSet,
    SingleModelViewSet,
)
from collectivo.version import __version__

from . import models, serializers

User = get_user_model()
Group = User.groups.field.related_model


class HealthView(APIView):
    """API view for health checks."""

    @extend_schema(responses={200: OpenApiResponse()})
    def get(self, request):
        """Return a 200 response."""
        return Response()


class AboutView(APIView):
    """API view for information about the collectivo instance."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: OpenApiResponse()})
    def get(self, request):
        """Return information about the collectivo instance."""
        data = {
            "version": __version__,
        }
        return Response(data)


class CoreSettingsViewSet(SingleModelViewSet):
    """Viewset for core settings."""

    queryset = models.CoreSettings.objects.all()
    serializer_class = serializers.CoreSettingsSerializer
    permission_classes = [ReadOrIsSuperuser]


class PermissionViewSet(ExtensionModelViewSet):
    """Viewset for endpoints."""

    queryset = models.Permission.objects.all()
    serializer_class = serializers.PermissionSerializer
    permission_classes = [IsSuperuser]
    filterset_class = get_filterset(serializers.PermissionSerializer)
    ordering_fields = get_ordering_fields(serializers.PermissionSerializer)


class PermissionGroupViewSet(ExtensionModelViewSet):
    """Viewset for endpoints."""

    queryset = models.PermissionGroup.objects.all()
    serializer_class = serializers.PermissionGroupSerializer
    permission_classes = [HasPerm]
    required_perms = {
        "GET": [("view_groups", "core")],
        "ALL": [("edit_groups", "core")],
    }
    filterset_class = get_filterset(serializers.PermissionGroupSerializer)
    ordering_fields = get_ordering_fields(
        serializers.PermissionGroupSerializer
    )

    def destroy(self, request, *args, **kwargs):
        """Delete a permission group."""
        instance = self.get_object()
        if instance.extension:
            return Response(
                {"detail": "This object is managed by an extension."},
                status=400,
            )
        return super().destroy(request, *args, **kwargs)


class PermissionGroupHistoryViewSet(HistoryViewSet):
    """Viewset for history of permission groups."""

    queryset = models.PermissionGroup.history.model.objects.all()
    serializer_class = serializers.PermissionGroupHistorySerializer
    permission_classes = [HasPerm]
    required_perms = {
        "GET": [("view_groups", "core")],
        "ALL": [("edit_groups", "core")],
    }
    filterset_class = get_filterset(
        serializers.PermissionGroupHistorySerializer
    )
    ordering_fields = get_ordering_fields(
        serializers.PermissionGroupHistorySerializer
    )


class UserViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Viewset for django users."""

    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [HasPerm]
    required_perms = {
        "GET": [("view_users", "core")],
        "ALL": [("edit_users", "core")],
    }
    filterset_class = get_filterset(serializers.UserSerializer)
    ordering_fields = get_ordering_fields(serializers.UserSerializer)


class UserHistoryViewSet(HistoryViewSet):
    """Viewset for history of users."""

    queryset = User.history.model.objects.all()
    serializer_class = serializers.UserHistorySerializer
    permission_classes = [HasPerm]
    required_perms = {
        "GET": [("view_users", "core")],
        "ALL": [("edit_users", "core")],
    }
    filterset_class = get_filterset(serializers.UserHistorySerializer)
    ordering_fields = get_ordering_fields(serializers.UserHistorySerializer)


class UserProfileViewSet(
    SchemaMixin,
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    """Viewset for django users to manage their own data."""

    queryset = User.objects.all()
    serializer_class = serializers.UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return queryset entry with the request's user."""
        return self.request.user


class UserProfilesViewSet(
    SchemaMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """Viewset for django users including all their profiles."""

    queryset = User.objects.all()
    serializer_class = serializers.UserProfilesSerializer
    permission_classes = [HasPerm]
    required_perms = {
        "GET": [("view_users", "core")],
    }
    filterset_class = get_filterset(serializers.UserProfilesSerializer)
    ordering_fields = get_ordering_fields(serializers.UserProfilesSerializer)

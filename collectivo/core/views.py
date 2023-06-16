"""Views of the core extension."""
from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from collectivo.utils.filters import get_filterset, get_ordering_fields
from collectivo.utils.mixins import HistoryMixin, SchemaMixin, SelfMixin
from collectivo.utils.permissions import IsSuperuser
from collectivo.utils.viewsets import ExtensionModelViewSet, SingleModelViewSet
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
    permission_classes = [IsSuperuser]


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
    permission_classes = [IsSuperuser]
    filterset_class = get_filterset(serializers.PermissionGroupSerializer)
    ordering_fields = get_ordering_fields(
        serializers.PermissionGroupSerializer
    )


class UserViewSet(SchemaMixin, HistoryMixin, viewsets.ModelViewSet):
    """Viewset for django users."""

    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [IsSuperuser]
    filterset_class = get_filterset(serializers.UserSerializer)
    ordering_fields = get_ordering_fields(serializers.UserSerializer)


class UserProfileViewSet(
    SchemaMixin,
    HistoryMixin,
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    """Viewset for django users including all their profiles."""

    queryset = User.objects.all()
    serializer_class = serializers.UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return queryset entry with the request's user."""
        return self.request.user


class UserProfilesViewSet(SchemaMixin, HistoryMixin, viewsets.ModelViewSet):
    """Viewset for django users including all their profiles."""

    queryset = User.objects.all()
    serializer_class = serializers.UserProfilesSerializer
    permission_classes = [IsSuperuser]
    filterset_class = get_filterset(serializers.UserProfilesSerializer)
    ordering_fields = get_ordering_fields(serializers.UserProfilesSerializer)


class GroupViewSet(SchemaMixin, HistoryMixin, viewsets.ModelViewSet):
    """Viewset for django groups."""

    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
    permission_classes = [IsSuperuser]
    filterset_class = get_filterset(serializers.GroupSerializer)
    ordering_fields = get_ordering_fields(serializers.GroupSerializer)

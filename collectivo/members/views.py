"""Views of the members extension."""
import logging
from rest_framework import viewsets, mixins
from rest_framework.exceptions import PermissionDenied
from collectivo.auth.permissions import IsAuthenticated
from collectivo.utils import get_auth_manager
from collectivo.views import SchemaMixin
from .permissions import IsMembersAdmin
from . import models, serializers
from .models import Member
from django.utils.timezone import localdate


logger = logging.getLogger(__name__)

member_fields = [field.name for field in models.Member._meta.get_fields()]

filterset_fields = {
    'first_name': ('contains', ),
    'last_name': ('contains', ),
    'person_type': ('exact', ),
    'membership_status': ('exact', ),
}


class MemberMixin(SchemaMixin, viewsets.GenericViewSet):
    """Base class for all member views."""

    queryset = models.Member.objects.all()

    def sync_user_data_with_auth(self, user_id, data):
        """Synchronize user data within authentication service."""
        if user_id is None:  # Member does not have a user account
            return
        auth_manager = get_auth_manager()
        new_user_data = {
            k: v for k, v in data.items()
            if k in auth_manager.get_user_fields()
        }
        auth_manager.update_user(user_id=user_id, **new_user_data)

        # Give user the role members user
        role = 'members_user'
        auth_manager = get_auth_manager()
        role_id = auth_manager.get_realm_role(role)['id']
        auth_manager.assign_realm_roles(
            user_id, {'id': role_id, 'name': role})

    def perform_create(self, serializer):
        """Create member and synchronize user data with auth service."""
        self.sync_user_data_with_auth(
            serializer.initial_data.get('user_id'),
            serializer.validated_data)
        serializer.save()

    def perform_update(self, serializer):
        """Update member and synchronize user data with auth service."""
        self.sync_user_data_with_auth(
            serializer.instance.user_id,
            serializer.validated_data)
        serializer.save()


class MemberRegisterViewSet(MemberMixin, mixins.CreateModelMixin):
    """
    API for members to register themselves.

    Requires authentication.
    """

    serializer_class = serializers.MemberRegisterSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Create member with user_id from auth token."""
        user_id = self.request.userinfo.user_id
        if Member.objects.filter(user_id=user_id).exists():
            raise PermissionDenied('User is already registered as a member.')
        self.sync_user_data_with_auth(user_id, serializer.validated_data)
        extra_fields = {
            'user_id': user_id,
            'membership_start': localdate(),
        }
        if 'tags' in serializer.validated_data:
            extra_fields['tags'] = serializer.validated_data['tags']
        serializer.save(**extra_fields)


class MemberProfileViewSet(
        MemberMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    """
    API for members to manage themselves.

    Requires authentication and registration.
    """

    serializer_class = serializers.MemberProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return member object of the currently authenticated user."""
        try:
            return self.queryset.get(user_id=self.request.userinfo.user_id)
        except Member.DoesNotExist:
            raise PermissionDenied('User is not registered as a member.')


class MembersSummaryViewSet(MemberMixin, mixins.ListModelMixin):
    """
    API for admins to get a summary of members.

    Requires the role 'members_admin'.
    """

    serializer_class = serializers.MemberSummarySerializer
    permission_classes = [IsMembersAdmin]
    filterset_fields = filterset_fields
    ordering_fields = member_fields


class MembersViewSet(MemberMixin, viewsets.ModelViewSet):
    """
    API for admins to manage members.

    Requires the role 'members_admin'.
    """

    serializer_class = serializers.MemberAdminSerializer
    permission_classes = [IsMembersAdmin]
    filterset_fields = filterset_fields
    ordering_fields = member_fields


class MemberTagViewSet(viewsets.ModelViewSet):
    """Manage member tags."""

    permission_classes = [IsMembersAdmin]
    serializer_class = serializers.MemberTagSerializer
    queryset = models.MemberTag.objects.all()


class MemberSkillViewSet(viewsets.ModelViewSet):
    """Manage member skills."""

    permission_classes = [IsMembersAdmin]
    serializer_class = serializers.MemberSkillSerializer
    queryset = models.MemberSkill.objects.all()


class MemberGroupViewSet(viewsets.ModelViewSet):
    """Manage member groups."""

    permission_classes = [IsMembersAdmin]
    serializer_class = serializers.MemberGroupSerializer
    queryset = models.MemberGroup.objects.all()


class MemberStatusViewSet(viewsets.ModelViewSet):
    """Manage member status."""

    permission_classes = [IsMembersAdmin]
    serializer_class = serializers.MemberStatusSerializer
    queryset = models.MemberStatus.objects.all()

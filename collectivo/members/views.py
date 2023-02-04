"""Views of the members extension."""
import logging
from rest_framework import viewsets, mixins
from rest_framework.exceptions import PermissionDenied, ValidationError
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
}


class MemberMixin(SchemaMixin, viewsets.GenericViewSet):
    """Base class for all member views."""

    queryset = models.Member.objects.all()

    def members_role(self):
        """Return representation of the members_user role."""
        auth_manager = get_auth_manager()
        role = 'members_user'
        role_id = auth_manager.get_realm_role(role)['id']
        return {'id': role_id, 'name': role}

    def assign_members_role(self, user_id):
        """Assign members_user role to user."""
        if user_id is None:
            return
        auth_manager = get_auth_manager()
        auth_manager.assign_realm_roles(user_id, self.members_role())

    def remove_members_role(self, user_id):
        """Remove members_user role from user."""
        if user_id is None:
            return
        auth_manager = get_auth_manager()
        auth_manager.delete_realm_roles_of_user(user_id, self.members_role())

    def sync_user_data(self, user_id, data):
        """Synchronize user data with auth service if user_id exists."""
        if user_id is None:
            return
        auth_manager = get_auth_manager()
        new_user_data = {
            k: v for k, v in data.items()
            if k in auth_manager.get_user_fields()
        }
        auth_manager.update_user(user_id=user_id, **new_user_data)

    def perform_create(self, serializer):
        """Create member and synchronize user data with auth service."""
        self.sync_user_data(
            serializer.initial_data.get('user_id'),
            serializer.validated_data)
        self.assign_members_role(serializer.initial_data.get('user_id'))
        serializer.save()

    def perform_update(self, serializer):
        """Update member and synchronize user data with auth service."""
        self.sync_user_data(
            serializer.instance.user_id, serializer.validated_data)
        serializer.save()

    def perform_destroy(self, instance):
        """Delete member and remove members_user role from auth service."""
        self.remove_members_role(instance.user_id)
        instance.delete()


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
        self.sync_user_data(user_id, serializer.validated_data)
        self.assign_members_role(user_id)
        extra_fields = {
            'user_id': user_id,
            'email': self.request.userinfo.email,
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


class MembersSudoViewSet(MemberMixin, viewsets.ModelViewSet):
    """
    API for admins to manage members.

    Requires the role 'members_admin'.
    """

    serializer_class = serializers.MemberSudoSerializer
    permission_classes = [IsMembersAdmin]
    filterset_fields = filterset_fields
    ordering_fields = member_fields


class MemberTagViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage member tags."""

    permission_classes = [IsMembersAdmin]
    serializer_class = serializers.MemberTagSerializer
    queryset = models.MemberTag.objects.all()

    def perform_destroy(self, instance):
        """Prevent deletion if assigned to members."""
        if instance.member_set.all().exists():
            raise ValidationError(
                'Cannot delete tag that is assigned to members.')
        return super().perform_destroy(instance)


class MemberSkillViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage member skills."""

    permission_classes = [IsMembersAdmin]
    serializer_class = serializers.MemberSkillSerializer
    queryset = models.MemberSkill.objects.all()


class MemberGroupViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage member groups."""

    permission_classes = [IsMembersAdmin]
    serializer_class = serializers.MemberGroupSerializer
    queryset = models.MemberGroup.objects.all()

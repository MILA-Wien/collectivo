"""Views of the members extension."""
import logging

from django.utils.timezone import localdate
from keycloak.exceptions import KeycloakDeleteError
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError

from collectivo.users.models import Role, User
from collectivo.users.permissions import IsAuthenticated
from collectivo.users.services import AuthService
from collectivo.utils.views import SchemaMixin

from . import models, serializers
from .models import Member
from .permissions import IsMembersAdmin

logger = logging.getLogger(__name__)

member_fields = [field.name for field in models.Member._meta.get_fields()]

filterset_fields = {
    "first_name": ("contains",),
    "last_name": ("contains",),
    "person_type": ("exact",),
}


class MemberMixin(SchemaMixin, viewsets.GenericViewSet):
    """Base class for all member views."""

    queryset = models.Member.objects.all()

    def create_member(self, serializer, user: User):
        """Create member and synchronize with users module."""
        if Member.objects.filter(user_id=user.user_id).exists():
            raise PermissionDenied("User is already registered as a member.")

        # Create member with extra data
        extra_fields = {
            "user_id": user.user_id,
            "email": user.email,
            "membership_start": localdate(),
        }
        if "tags" in serializer.validated_data:
            extra_fields["tags"] = serializer.validated_data["tags"]
        serializer.save(**extra_fields)

        # Send welcome mail
        try:
            from collectivo.members.emails.models import (
                EmailAutomation,
                EmailCampaign,
            )
            from collectivo.members.emails.views import EmailCampaignViewSet
            from collectivo.utils import register_viewset

            automations = EmailAutomation.objects.filter(trigger="new_member")

            for automation in automations:
                member = serializer.instance
                campaign = {
                    "recipients": [member.id],
                    "template": automation.template.id,
                    "send": True,
                }
                res = register_viewset(EmailCampaignViewSet, payload=campaign)

                # Add automation to campaign for documentation
                campaign = EmailCampaign.objects.get(id=res.data["id"])
                campaign.automation = automation
                campaign.save()

        except ImportError:
            # Email Module not installed
            pass

    def perform_update(self, serializer):
        """Update member and synchronize user data with auth service."""
        user = User.objects.get(user_id=serializer.instance.user_id)
        user.first_name = serializer.validated_data["first_name"]
        user.last_name = serializer.validated_data["last_name"]
        user.email = serializer.validated_data["email"]
        user.save()
        serializer.save()

    def perform_destroy(self, instance):
        """Delete member and remove members_user role from auth service."""
        user = User.objects.get(user_id=instance.user_id)
        user.roles.remove(Role.objects.get_or_create(name="members_user")[0])
        user.save()
        instance.delete()


class MemberRegisterViewSet(MemberMixin, mixins.CreateModelMixin):
    """
    API for members to register themselves.

    Requires authentication.
    """

    serializer_class = serializers.MemberRegisterSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Create member with authenticated user."""
        self.create_member(serializer, self.request.auth_user)


class MemberProfileViewSet(
    MemberMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
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
            raise PermissionDenied("User is not registered as a member.")


class MembersSummaryViewSet(MemberMixin, mixins.ListModelMixin):
    """
    API for admins to get a summary of members.

    Requires the role 'members_admin'.
    """

    serializer_class = serializers.MemberSummarySerializer
    permission_classes = [IsMembersAdmin]
    filterset_fields = filterset_fields
    ordering_fields = member_fields


class MembersAdminViewSet(
    MemberMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    API for admins to manage members.

    Requires the role 'members_admin'.
    """

    serializer_class = serializers.MemberAdminSerializer
    permission_classes = [IsMembersAdmin]
    filterset_fields = filterset_fields
    ordering_fields = member_fields


class MembersAdminCreateViewSet(MemberMixin, mixins.CreateModelMixin):
    """
    API for admins to create members.

    Requires the role 'members_admin'.
    """

    serializer_class = serializers.MemberAdminCreateSerializer
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
                "Cannot delete tag that is assigned to members."
            )
        return super().perform_destroy(instance)

    def get_permissions(self):
        """Set permissions for this viewset."""
        if self.action == "list":
            return [IsAuthenticated()]
        return [IsMembersAdmin()]


class MemberSkillViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage member skills."""

    serializer_class = serializers.MemberSkillSerializer
    queryset = models.MemberSkill.objects.all()

    def get_permissions(self):
        """Set permissions for this viewset."""
        if self.action == "list":
            return [IsAuthenticated()]
        return [IsMembersAdmin()]


class MemberGroupViewSet(SchemaMixin, viewsets.ModelViewSet):
    """Manage member groups."""

    permission_classes = [IsMembersAdmin]
    serializer_class = serializers.MemberGroupSerializer
    queryset = models.MemberGroup.objects.all()

    def get_permissions(self):
        """Set permissions for this viewset."""
        if self.action == "list":
            return [IsAuthenticated()]
        return [IsMembersAdmin()]

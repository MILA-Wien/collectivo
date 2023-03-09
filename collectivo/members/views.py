"""Views of the members extension."""
import logging

from django.contrib.auth import get_user_model
from django.utils.timezone import localdate
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from collectivo.core.permissions import HasGroup
from collectivo.utils.views import SchemaMixin

from . import models, serializers
from .models import Member

logger = logging.getLogger(__name__)

User = get_user_model()

member_fields = [field.name for field in models.Member._meta.get_fields()]

filterset_fields = {}  # TODO: These are redefined in another branch


class MemberMixin(SchemaMixin, viewsets.GenericViewSet):
    """Base class for all member views."""

    queryset = models.Member.objects.all()

    def create_member(self, serializer, user):
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
            from collectivo.emails.models import EmailAutomation, EmailCampaign
            from collectivo.emails.views import EmailCampaignViewSet
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

    def perform_destroy(self, instance):
        """Delete member and remove members_user role from auth service."""
        # TODO instance.user.roles.remove(Role.objects.get_or_create
        # (name="members_user")[0])
        # instance.user.save()
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
            return self.queryset.get(user=self.request.user)
        except Member.DoesNotExist:
            raise PermissionDenied("User is not registered as a member.")


class MembersViewSet(
    MemberMixin,
    mixins.CreateModelMixin,
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
    permission_classes = [HasGroup]
    required_groups = ["collectivo.members.admin"]
    filterset_fields = filterset_fields
    ordering_fields = member_fields + ["user__first_name", "user__last_name"]

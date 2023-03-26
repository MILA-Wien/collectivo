"""Tests of the history models of the members extension."""
from django.contrib.auth import get_user_model
from django.db.models import signals
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.utils.test import create_testuser

from ..profiles.models import MemberProfile
from .filters import MEMBER, MEMBERS_URL

User = get_user_model()

HISTORY_URL = "collectivo:collectivo.members:member-history"


class MembersHistoryTests(TestCase):
    """Test the history functions of the members extension."""

    def setUp(self):
        """Create member for testing."""
        signals.post_save.disconnect(
            sender=User, dispatch_uid="update_keycloak_user"
        )
        self.client = APIClient()
        self.superuser = create_testuser(superuser=True)
        self.client.force_authenticate(self.superuser)

    def list_changes(self, obj):
        """List the changes of a historical model."""
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)
            changed_fields = [change.field for change in delta.changes]
            change_summary = {
                change.field: (change.old, change.new)
                for change in delta.changes
            }
        else:
            field_objs = obj._meta.get_fields()
            changed_fields = [
                field.name
                for field in field_objs
                if getattr(obj, field.name) and "history" not in field.name
            ]
            change_summary = {
                field: getattr(obj, field) for field in changed_fields
            }
        return changed_fields, change_summary

    def test_history(self):
        """Test the history of a member."""

        # Create an object as superuser
        user = User.objects.create_user(username="test")
        payload = {**MEMBER, "user": user.id}
        self.client.post(MEMBERS_URL, payload)

        # Test the history of the creation
        member = MemberProfile.objects.get(user=user)
        historic_member = member.history.first()
        self.assertEqual(historic_member.get_history_type_display(), "Created")
        self.assertEqual(historic_member.history_user.id, self.superuser.id)

        # Create an update through backend (no user)
        member.address_door = "1"
        member.address_city = "new city"
        member.save()
        self.assertEqual(len(member.history.all()), 2)

        # Test the history of the update
        historic_member = member.history.first()
        self.assertEqual(historic_member.get_history_type_display(), "Changed")
        self.assertEqual(historic_member.history_user, None)
        changed_fields, _ = self.list_changes(historic_member)
        for field in ["address_door", "address_city"]:
            self.assertIn(field, changed_fields)

    def test_history_api(self):
        """Test getting the history of an object for a user."""

        # Create an object as superuser
        user = User.objects.create_user(username="test")
        payload = {**MEMBER, "user": user.id}
        self.client.post(MEMBERS_URL, payload)

        path = reverse(HISTORY_URL, args=[user.id])
        res = self.client.get(path)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data[0]["history_user"], self.superuser.id)

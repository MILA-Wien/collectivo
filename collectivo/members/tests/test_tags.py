"""Test the features of the emails API."""
from django.test import TestCase
from django.urls import reverse
from collectivo.auth.clients import CollectivoAPIClient
from collectivo.auth.userinfo import UserInfo
from collectivo.members.models import Member, MemberTag
import json


TAGS_URL = reverse('collectivo:collectivo.members:tag-list')
TAG_URL_NAME = 'collectivo:collectivo.members:tag-detail'
MEMBER_URL = reverse('collectivo:collectivo.members:member-detail', args=[1])


class MembersTagsTests(TestCase):
    """Test the members tags API."""

    def setUp(self):
        """Prepare test case."""
        self.client = CollectivoAPIClient()
        self.client.force_authenticate(
            UserInfo(is_authenticated=True, roles=['members_admin'])
        )

    def assign_tag(self):
        """Assign a tag to a member."""
        res = self.client.post(TAGS_URL, {'label': 'test tag'})
        tag_id = res.data['id']
        self.client.patch(MEMBER_URL, {'tags': [tag_id]})
        return tag_id

    def unassign_tag(self, tag_id):
        """Unassign a tag from a member."""
        self.client.patch(
            MEMBER_URL, json.dumps({'tags': []}),
            content_type="application/json")

    def test_tag_assign(self):
        """Test assigning a tag to a member."""
        self.assign_tag()
        self.assertEqual(MemberTag.objects.filter(label='test tag').count(), 1)
        self.assertEqual(Member.objects.get(pk=1).tags.count(), 1)

    def test_tag_delete_denied(self):
        """Test deleting a tag is denied if it is assigned to a member."""
        tag_id = self.assign_tag()
        tags_url = reverse(TAG_URL_NAME, args=[tag_id])
        res = self.client.delete(tags_url)
        self.assertEqual(res.status_code, 400)

    def test_tag_delete_accepted(self):
        """Test deleting a tag is accepted if it is not used anywhere."""
        tag_id = self.assign_tag()
        self.unassign_tag(tag_id)
        self.assertEqual(Member.objects.get(pk=1).tags.count(), 0)
        tags_url = reverse(TAG_URL_NAME, args=[tag_id])
        res = self.client.delete(tags_url)
        self.assertEqual(res.status_code, 204)

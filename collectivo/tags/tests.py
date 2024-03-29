"""Tests for the tags extension."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from collectivo.utils.test import create_testuser

from .models import Tag

TAGS_URL = reverse("collectivo.tags:tag-list")
TAG_URL_NAME = "collectivo.tags:tag-detail"
TAG_PROFILES_NAME = "collectivo.tags:profile-detail"
User = get_user_model()


class TagsTests(TestCase):
    """Tests for the tags extension."""

    def setUp(self):
        """Prepare test case."""
        self.client = APIClient()
        self.user = create_testuser(superuser=True)
        self.client.force_authenticate(self.user)
        self.tag = Tag.objects.create(name="test_tag")

    def test_bulk_edit_tags(self):
        """Test bulk edit functionality."""
        pass

    def test_get_tags(self):
        """Test getting tags."""
        res = self.client.get(TAGS_URL + "?offset=0&limit=10")
        self.assertEqual(res.status_code, 200)

    def assign_tag(self):
        """Assign a tag to a user."""
        self.tag.users.add(self.user)
        self.tag.save()

    def unassign_tag(self):
        """Unassign a tag from a user."""
        self.tag.users.remove(self.user)
        self.tag.save()

    def test_tag_assign(self):
        """Test assigning a tag to a member."""
        self.assign_tag()
        self.assertTrue(self.user.tags.filter(name="test_tag").exists())

    def test_tag_delete_denied(self):
        """Test deleting a tag is denied if it is assigned to a member."""
        self.assign_tag()
        tags_url = reverse(TAG_URL_NAME, args=[self.tag.pk])
        res = self.client.delete(tags_url)
        self.assertEqual(res.status_code, 400)

    def test_tag_delete_accepted(self):
        """Test deleting a tag is accepted if it is not used anywhere."""
        self.assign_tag()
        self.unassign_tag()
        self.assertFalse(self.user.tags.filter(name="test_tag").exists())
        tags_url = reverse(TAG_URL_NAME, args=[self.tag.pk])
        res = self.client.delete(tags_url)
        self.assertEqual(res.status_code, 204)

    def test_tag_profile(self):
        """Test getting a tag profile."""
        self.assign_tag()
        res = self.client.get(reverse(TAG_PROFILES_NAME, args=[self.user.pk]))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["tags"], [self.tag.pk])

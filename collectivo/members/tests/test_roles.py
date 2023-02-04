"""Tests of the interaction between members and the auth service."""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from collectivo.utils import get_auth_manager
from ..models import Member

MEMBERS_URL = reverse('collectivo:collectivo.members:member-list')
MEMBER_URL_LABEL = 'collectivo:collectivo.members:member-detail'
PROFILE_URL = reverse('collectivo:collectivo.members:profile')
REGISTER_URL = reverse('collectivo:collectivo.members:register')
REGISTRATION_SCHEMA_URL = reverse(
    'collectivo:collectivo.members:register-schema')
PROFILE_SCHEMA_URL = reverse('collectivo:collectivo.members:profile-schema')


class MemberAuthSyncTests(TestCase):
    """Test data synchronization with keycloak."""

    def setUp(self):
        """Prepare test case."""
        self.client = APIClient()
        self.keycloak = get_auth_manager()
        self.member_id = 2
        self.email = 'test_superuser@example.com'
        self.token = self.keycloak.openid.token(self.email, 'Test123!')
        self.access_token = self.token['access_token']
        self.client.credentials(HTTP_AUTHORIZATION=self.access_token)

    def tearDown(self):
        """Reset user data of auth service."""
        res = self.client.patch(
            reverse(MEMBER_URL_LABEL, args=[self.member_id]),
            {'first_name': 'Test Member 01'}
        )
        if res.status_code != 200:
            raise ValueError("API call failed: ", res.content)

    def test_auth_sync_as_admin(self):
        """Test that auth fields are updated on auth server for /members."""
        # Patch the name of a member
        res2 = self.client.patch(
            reverse(MEMBER_URL_LABEL, args=[self.member_id]),
            {'first_name': 'new_name'}
        )
        if res2.status_code != 200:
            raise ValueError("API call failed: ", res2.content)

        # Check that new attribute is set on django
        member = Member.objects.get(id=self.member_id)
        self.assertEqual(
            getattr(member, 'first_name'), 'new_name')

        # Check that new attribute is set on keycloak
        userinfo = self.keycloak.get_user(res2.data['user_id'])
        self.assertEqual(userinfo['firstName'], 'new_name')

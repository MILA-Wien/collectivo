"""Tests of the interaction between members and the auth service."""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from collectivo.utils import get_auth_manager
from ..models import Member
from .test_members import TEST_MEMBER_POST
from jwt import decode

MEMBERS_URL = reverse('collectivo:collectivo.members:member-list')
MEMBER_URL_LABEL = 'collectivo:collectivo.members:member-detail'
PROFILE_URL = reverse('collectivo:collectivo.members:profile')
REGISTER_URL = reverse('collectivo:collectivo.members:register')
PROFILE_SCHEMA_URL = reverse('collectivo:collectivo.members:profile-schema')


class MemberAuthSyncTests(TestCase):
    """Test data synchronization with keycloak."""

    def get_token(self, email):
        """Get decoded auth token for user."""
        token = self.keycloak.openid.token(email, 'Test123!')
        access_token = token['access_token']
        return token, decode(access_token, options={"verify_signature": False})

    def setUp(self):
        """Prepare test case."""
        self.client = APIClient()
        self.keycloak = get_auth_manager()
        self.member_id = 2
        self.email = 'test_superuser@example.com'
        self.token = self.keycloak.openid.token(self.email, 'Test123!')
        self.access_token = self.token['access_token']
        self.client.credentials(HTTP_AUTHORIZATION=self.access_token)

        self.user_client = APIClient()
        self.user_email = 'test_user_not_member@example.com'
        token, data = self.get_token(self.user_email)
        self.user_id = data.get('sub', None)
        self.user_client.credentials(HTTP_AUTHORIZATION=token['access_token'])

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
        self.assertEqual(res2.status_code, 200)

        # Check that new attribute is set on django
        member = Member.objects.get(id=self.member_id)
        self.assertEqual(
            getattr(member, 'first_name'), 'new_name')

        # Check that new attribute is set on keycloak
        userinfo = self.keycloak.get_user(res2.data['user_id'])
        self.assertEqual(userinfo['firstName'], 'new_name')

    def test_register_member_assigns_members_user_role(self):
        """Test that new members receive the auth role 'members_user'."""
        # Create a new member
        res = self.user_client.post(REGISTER_URL, TEST_MEMBER_POST)
        self.assertEqual(res.status_code, 201)
        _, data = self.get_token(self.user_email)
        self.assertIn('members_user', data['realm_access']['roles'])

        # Delete the member again
        res = self.client.delete(
            reverse(MEMBER_URL_LABEL, args=[res.data['id']]))
        self.assertEqual(res.status_code, 204)
        _, data = self.get_token(self.user_email)
        self.assertNotIn('members_user', data['realm_access']['roles'])

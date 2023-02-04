"""Tests of the members API."""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from collectivo.auth.clients import CollectivoAPIClient
from collectivo.auth.userinfo import UserInfo
from collectivo.utils import get_auth_manager
from django.utils.timezone import localdate
from ..models import Member


MEMBERS_URL = reverse('collectivo:collectivo.members:member-list')
MEMBER_URL_LABEL = 'collectivo:collectivo.members:member-detail'
PROFILE_URL = reverse('collectivo:collectivo.members:profile')
REGISTER_URL = reverse('collectivo:collectivo.members:register')
REGISTRATION_SCHEMA_URL = reverse(
    'collectivo:collectivo.members:register-schema')
PROFILE_SCHEMA_URL = reverse('collectivo:collectivo.members:profile-schema')

TEST_MEMBER = {
    'first_name': 'firstname',
    'last_name': 'lastname',
    'gender': 'diverse',
    'address_street': 'my street',
    'address_number': '1',
    'address_postcode': '0000',
    'address_city': 'my city',
    'address_country': 'my country',
    'shares_number': 9,
}

TEST_MEMBER_POST = {
    **TEST_MEMBER,
    'person_type': 'natural',
    'membership_type': 'active',
    'email_verified': True,
    'survey_contact': '-',
    'survey_motivation': '-',
    'shares_payment_type': 'sepa',
    'statutes_approved': True,
    'shares_tarif': 'normal'
}

TEST_MEMBER_GET = {
    **TEST_MEMBER,
    'membership_start': localdate(),
    'email': 'some_member@example.com',
}

TEST_USER = {
    'email': 'some_member@example.com',
    'username': 'some_member@example.com',
    'firstName': 'firstname',
    'lastName': 'lastname',
    "enabled": True,
    "emailVerified": True,
}


class PublicMemberApiTests(TestCase):
    """Test the public members API."""

    def setUp(self):
        """Prepare client."""
        self.client = APIClient()

    def test_auth_required_for_members(self):
        """Test that authentication is required for /members."""
        res = self.client.get(MEMBERS_URL)
        self.assertEqual(res.status_code, 403)

    def test_auth_required_for_me(self):
        """Test that authentication is required for /profile."""
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, 403)


class MembersTestCase(TestCase):
    """Template for test cases that need an authorized user."""

    def setUp(self):
        """Create client with authorized test user."""
        self.auth_manager = get_auth_manager()
        user_id = self.auth_manager.create_user(TEST_USER, exist_ok=True)
        self.auth_manager.set_user_password(  # noqa
                user_id, password='Test123!', temporary=False)  # noqa
        self.client = APIClient()
        self.authorize()

    def tearDown(self):
        """Delete test user."""
        auth_manager = get_auth_manager()
        user_id = auth_manager.get_user_id('some_member@example.com')
        auth_manager.delete_user(user_id)

    def authorize(self):
        """Authorize test user."""
        token = self.auth_manager.openid.token(
            'some_member@example.com', 'Test123!')
        self.client.credentials(HTTP_AUTHORIZATION=token['access_token'])


class MemberRegistrationTests(MembersTestCase):
    """Test the private members API for users that are not members."""

    def test_cannot_access_profile(self):
        """Test that a user cannot access API if they are not a member."""
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.data['detail'],
                         'User is not registered as a member.')

    def create_member(self, payload=TEST_MEMBER_POST):
        """Create a sample member."""
        res = self.client.post(REGISTER_URL, payload)
        if res.status_code != 201:
            raise ValueError('Could not register member:', res.content)
        member = Member.objects.get(id=res.data['id'])
        return member

    def test_create_member(self):
        """Test that an authenticated user can create itself as a member."""
        member = self.create_member()
        for key, value in TEST_MEMBER_GET.items():
            self.assertEqual(value, getattr(member, key))

    def test_create_legal_member(self):
        """Test that a legal member automatically becomes type investing."""
        payload = {**TEST_MEMBER_POST, 'person_type': 'legal'}
        member = self.create_member(payload)
        self.assertEqual(member.membership_type, 'investing')

    def test_create_member_tags_missing(self):
        """Test that unchecked tag fields do not become tags."""
        member = self.create_member()
        self.assertFalse(
            member.tags.filter(label='Public use approved').exists())

    def test_create_member_tags(self):
        """Test that checked tag fields become tags."""
        payload = {**TEST_MEMBER_POST, 'public_use_approved': True}
        member = self.create_member(payload)
        self.assertTrue(
            member.tags.filter(label='Public use approved').exists())

    def test_multiple_choice_str(self):
        """Test that multiple choices can be selected with strings."""
        payload = {**TEST_MEMBER_POST, 'groups_interested': ['1', '2', '3']}
        member = self.create_member(payload)
        group_ids = [group.id for group in member.groups_interested.all()]
        self.assertEqual(group_ids, [1, 2, 3])

    def test_multiple_choice_with_int(self):
        """Test that multiple choices can be selected with numbers."""
        payload = {**TEST_MEMBER_POST, 'groups_interested': [1, 2, 3]}
        member = self.create_member(payload)
        group_ids = [group.id for group in member.groups_interested.all()]
        self.assertEqual(group_ids, [1, 2, 3])


class PrivateMemberApiTestsForMembers(MembersTestCase):
    """Test the private members API for users that are members."""

    def setUp(self):
        """Register authorized user as member."""
        super().setUp()
        res = self.client.post(REGISTER_URL, TEST_MEMBER_POST)
        if res.status_code != 201:
            raise Exception('Could not register member:', res.content)
        self.members_id = res.data['id']

    def test_member_cannot_access_admin_area(self):
        """Test that a normal member cannot access admin API."""
        res = self.client.get(MEMBERS_URL)
        self.assertEqual(res.status_code, 403)

    def test_cannot_create_same_member_twice(self):
        """Test that a member cannot create itself as a member again."""
        res2 = self.client.post(REGISTER_URL, TEST_MEMBER_POST)
        self.assertEqual(res2.status_code, 403)

    def test_get_profile(self):
        """Test that a member can view it's own data."""
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, 200)
        for key, value in TEST_MEMBER_GET.items():
            self.assertEqual(str(value), str(res.data[key]))

    def test_update_member(self):
        """Test that a member can edit non-admin fields of it's own data."""
        self.client.patch(PROFILE_URL, {'address_street': 'my_street'})
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.data['address_street'], 'my_street')

    def test_update_member_admin_fields_fails(self):
        """Test that a member cannot edit admin fields of it's own data."""
        self.client.patch(PROFILE_URL, {'admin_notes': 'my note'})
        member = Member.objects.get(id=self.members_id)
        self.assertNotEqual(
            getattr(member, 'admin_notes'), 'my note')

    def test_members_profile_schema(self):
        """Test that the schema for members registration is correct."""
        res = self.client.get(PROFILE_SCHEMA_URL)
        self.assertTrue('birthday' not in res.data)
        self.assertEqual(res.data['first_name']['read_only'], True)
        self.assertEqual(res.data['first_name']['required'], False)
        self.assertEqual(res.data['address_street']['required'], True)


class PrivateMemberApiTestsForAdmins(TestCase):
    """Test the privatly available members API for admins."""

    def setUp(self):
        """Prepare client, extension, & micro-frontend."""
        self.client = CollectivoAPIClient()
        Member.objects.all().delete()
        user = UserInfo(
            roles=['members_admin'],
            is_authenticated=True,
        )
        self.client.force_authenticate(user)

    def create_members(self):
        """Create an unordered set of members for testing."""
        for i in [0, 2, 1]:
            payload = {**TEST_MEMBER_POST, 'first_name': str(i)}
            res = self.client.post(MEMBERS_URL, payload)
            if res.status_code != 201:
                raise ValueError("Create members failed: ", res.content)

    def test_create_members(self):
        """Test that admins can create members."""
        self.create_members()
        self.assertEqual(len(Member.objects.all()), 3)

    def test_update_member_admin_fields(self):
        """Test that admins can write to admin fields."""
        res1 = self.client.post(MEMBERS_URL, TEST_MEMBER_POST)
        self.assertEqual(res1.status_code, 201)
        res2 = self.client.patch(
            reverse(
                'collectivo:collectivo.members:member-detail',
                args=[res1.data['id']]), {'admin_notes': 'my note'}
        )
        if res2.status_code != 200:
            raise ValueError("API call failed: ", res2.content)
        member = Member.objects.get(id=res1.data['id'])
        self.assertEqual(
            getattr(member, 'admin_notes'), 'my note')

    def test_member_sorting(self):
        """Test that all member fields can be sorted."""
        self.create_members()

        res = self.client.get(MEMBERS_URL+'?ordering=first_name')
        self.assertEqual(
            [entry['first_name'] for entry in res.data],
            ['0', '1', '2']
        )

        res = self.client.get(MEMBERS_URL+'?ordering=-first_name')
        self.assertEqual(
            [entry['first_name'] for entry in res.data],
            ['2', '1', '0']
        )

    def test_member_filtering(self):
        """Test that member names can be filtered with 'contains'."""
        self.create_members()

        res = self.client.get(MEMBERS_URL+'?first_name__contains=1')
        self.assertEqual(
            [entry['first_name'] for entry in res.data],
            ['1']
        )

    def test_member_pagination(self):
        """Test that pagination works for members."""
        for _ in range(3):
            self.create_members()

        limit = 3
        offset = 5
        res = self.client.get(
            MEMBERS_URL+f'?limit={limit}&offset={offset}')

        self.assertEqual(
            [m.id for m in Member.objects.all()][offset:offset+limit],
            [m['id'] for m in res.data['results']]
        )

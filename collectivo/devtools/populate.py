"""Populate collectivo & keycloak with test users."""
import logging
from collectivo.utils import get_auth_manager, register_viewset
from collectivo.members.views import MembersAdminCreateViewSet
from collectivo.members.models import Member
from keycloak.exceptions import KeycloakGetError, KeycloakDeleteError


logger = logging.getLogger(__name__)

N_TEST_MEMBERS = 3


# Add users
superusers = [
    {
        "email": "test_superuser@example.com",
        "username": "test_superuser@example.com",
        "enabled": True,
        "firstName": "Test Superuser",
        "lastName": "Example",
        "emailVerified": True,
    },
]

members = [
    {
        "email": f"test_member_{str(i).zfill(2)}@example.com",
        "username": f"test_member_{str(i).zfill(2)}@example.com",
        "enabled": True,
        "firstName": f"Test Member {str(i).zfill(2)}",
        "lastName": "Example",
        "emailVerified": True,
    }
    for i in range(1, N_TEST_MEMBERS+1)
] + superusers

users = [
    {
        "email": "test_user_not_verified@example.com",
        "username": "test_user_not_verified@example.com",
        "enabled": True,
        "firstName": "Example",
        "lastName": "Example",
        "emailVerified": False
    },
    {
        "email": "test_user_not_member@example.com",
        "username": "test_user_not_member@example.com",
        "enabled": True,
        "firstName": "Example",
        "lastName": "Example",
        "emailVerified": True
    },
] + members


def populate_keycloak_with_test_data():
    """Add users, groups, and roles to keycloak."""
    logger.debug('Creating test-population')
    auth_manager = get_auth_manager()

    for user in users:
        try:
            user_id = auth_manager.get_user_id(user['email'])
            auth_manager.delete_user(user_id)
            Member.objects.filter(email=user['email']).delete()
        except (KeycloakGetError, KeycloakDeleteError):
            pass
        user_id = auth_manager.create_user(
            user['firstName'], user['lastName'], user['email'],
            email_verified=user['emailVerified'])
        auth_manager.set_user_password(  # noqa
            user_id, password='Test123!', temporary=False)  # noqa

    # Assign superuser role to superusers
    for user in superusers:
        roles = ('superuser', 'members_admin', 'shifts_admin')
        for role in roles:
            user_id = auth_manager.get_user_id(user['email'])
            role_id = auth_manager.get_realm_role(role)['id']
            auth_manager.assign_realm_roles(
                user_id, {'id': role_id, 'name': role})

    # Make members into members
    # This automatically adds them to the group 'members'
    for member in members:
        user_id = auth_manager.get_user_id(member['email'])
        payload = {
            'email': member['email'],  # To match with keycloak user
            'first_name': member['firstName'],
            'last_name': member['lastName'],
            'gender': 'diverse',
            'address_street': 'My street',
            'address_number': '5',
            'address_stair': 'A',
            'address_door': '8',
            'address_postcode': '1230',
            'address_city': 'Wien',
            'address_country': 'Österreich',
            'phone': '066003745385',
            'membership_start': '2022-12-08',
            'person_type': 'natural',
            'membership_type': 'active',
            'shares_number': 5,
            'shares_tarif': 'normal',
            'shares_payment_type': 'sepa',
            'statutes_approved': True,
        }
        if member['email'] == 'test_member_02@example.com':
            payload['person_type'] = 'legal'

        register_viewset(
            MembersAdminCreateViewSet,
            payload=payload
        )

"""Populate collectivo & keycloak with test users."""
import logging
from collectivo.utils import get_auth_manager, register_viewset
from collectivo.members.views import MembersAdminViewSet
from keycloak.exceptions import KeycloakGetError


logger = logging.getLogger(__name__)

N_TEST_MEMBERS = 15


# Add users
superusers = [
    {
        "email": "test_superuser@example.com",
        "username": "test_superuser@example.com",
        "enabled": True,
        "firstName": "Example",
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
        "emailVerified": True
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
        except KeycloakGetError:
            pass
        user_id = auth_manager.create_user(user)
        auth_manager.set_user_password(  # noqa
            user_id, password='test', temporary=False)  # noqa

    # Assign superuser role to superusers
    for user in superusers:
        role = 'superuser'
        user_id = auth_manager.get_user_id(user['email'])
        role_id = auth_manager.get_realm_role(role)['id']
        auth_manager.assign_realm_roles(
            user_id, {'id': role_id, 'name': role})

    # Make members into members
    # This automatically adds them to the group 'members'
    for member in members:
        user_id = auth_manager.get_user_id(member['username'])
        payload = {
            'user_id': user_id,

            'email': member['email'],
            'email_verified': member['emailVerified'],

            'first_name': member['firstName'],
            'last_name': member['lastName'],
        }
        register_viewset(
            MembersAdminViewSet,
            payload=payload
        )

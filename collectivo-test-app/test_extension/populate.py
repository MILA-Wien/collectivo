"""Populate collectivo & keycloak with test users."""
import logging
from collectivo.auth.manager import KeycloakManager
from collectivo.members.models import Member
from keycloak.exceptions import KeycloakPostError


logger = logging.getLogger(__name__)

N_TEST_MEMBERS = 15


def populate_keycloak_with_test_data():
    """Add users, groups, and roles to keycloak."""
    try:
        logger.debug('Creating test-population')
        _populate_keycloak_with_test_data()
    except Exception as e:
        logger.debug(f'Failed to create test-population: {repr(e)}')


def _populate_keycloak_with_test_data():
    """Add users, groups, and roles to keycloak."""
    keycloak_admin = KeycloakManager().keycloak_admin

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
        for i in range(1, N_TEST_MEMBERS)
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

    for user in users:
        try:
            user_id = keycloak_admin.create_user(user, exist_ok=True)
            keycloak_admin.set_user_password(  # noqa
                user_id, password='test', temporary=False)  # noqa
        except KeycloakPostError:
            pass

    # Add groups to users
    groups_and_users = {
        'superusers': [d['email'] for d in superusers],
    }
    for group_name, user_names in groups_and_users.items():
        group_id = keycloak_admin.get_group_by_path(f'/{group_name}')['id']
        for user_name in user_names:
            user_id = keycloak_admin.get_user_id(user_name)
            keycloak_admin.group_user_add(user_id, group_id)

    # Make members into members
    # This automatically adds them to the group 'members'
    for member in members:
        user_id = keycloak_admin.get_user_id(member['username'])
        Member.objects.get_or_create(user_id=user_id)
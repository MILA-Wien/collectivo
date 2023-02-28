"""Utility functions for the tests of the users module."""
from django.urls import reverse

from collectivo.users.models import Role, User

from .fixtures import PASSWORD, TEST_USER


def create_test_user(roles):
    """Create a test user."""
    user = User.objects.create(**TEST_USER)
    user.set_password(PASSWORD, temporary=False)
    user.set_email_verified(True)
    for role_name in roles:
        role = Role.objects.get_or_create(name=role_name)[0]
        user.roles.add(role)
    user.save()
    return user

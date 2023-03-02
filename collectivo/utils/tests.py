"""Tests for the collectivo utility functions."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


def create_testuser(
    groups: list[str] = None,
    superuser: bool = False,
) -> tuple[APIClient, User]:
    """Return a user given groups."""
    try:
        User.objects.get(username="testuser").delete()
    except User.DoesNotExist:
        pass
    user = User.objects.create_user(username="testuser")
    groups = groups or []
    if superuser and "collectivo.core.admin" not in groups:
        groups.append("collectivo.core.admin")
    for group in groups:
        user.groups.add(Group.objects.get_or_create(name=group)[0])
    return user


class UtilsTests(TestCase):
    """Test collectivo utility functions."""

    pass

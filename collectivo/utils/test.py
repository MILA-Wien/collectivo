"""Tests for the collectivo utility functions."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

User = get_user_model()


def create_testuser(
    username="testuser",
    groups: list[str] = None,
    superuser: bool = False,
) -> tuple[APIClient, User]:
    """Return a user with given groups."""
    try:
        User.objects.get(username=username).delete()
    except User.DoesNotExist:
        pass
    user = User.objects.create_user(username=username)
    groups = groups or []
    if superuser and "collectivo.core.admin" not in groups:
        groups.append("collectivo.core.admin")
    for group in groups:
        user.groups.add(Group.objects.get_or_create(name=group)[0])
    return user


def create_testadmin(
    username="testadmin",
    groups: list[str] = None,
    superuser: bool = True,
) -> tuple[APIClient, User]:
    """Return a superuser with given groups."""
    return create_testuser(username, groups, superuser)

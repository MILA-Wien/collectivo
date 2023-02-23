"""Setup functions for the users module."""
from collectivo.users.models import Role


def create_groups_and_roles():
    """Add default roles."""

    Role.objects.get_or_create(name="superuser")

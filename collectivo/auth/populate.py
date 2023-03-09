"""Populate auth service with groups and roles."""
import logging
from collectivo.utils import get_auth_manager


logger = logging.getLogger(__name__)


def create_groups_and_roles():
    """Add groups and roles to auth service."""
    logger.debug("Creating roles")
    auth_manager = get_auth_manager()

    # TODO Get automatically from extensions
    roles = [
        "superuser",
        "members_user",
        "members_admin",
        "shifts_user",
        "shifts_admin",
        "direktkredit_user",
        "direktkredit_admin",
    ]

    # Create roles
    for role in roles:
        auth_manager.create_realm_role(
            payload={"name": role}, skip_exists=True
        )

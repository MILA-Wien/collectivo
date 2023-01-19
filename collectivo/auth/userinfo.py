"""Userinfo class of the authentication module."""
import logging


logger = logging.getLogger(__name__)


class UserInfo:
    """Class for storing information about a user."""

    def __init__(self,
                 user_id: str = None,
                 email: str = None,
                 email_verified: bool = False,
                 is_authenticated: bool = False,
                 first_name: str = None,
                 last_name: str = None,
                 roles: list[str] = None):
        """Initialize object."""
        self.user_id = user_id
        self.email = email
        self.email_verified = email_verified
        self.is_authenticated = is_authenticated
        self.first_name = first_name
        self.last_name = last_name
        self.roles = roles if roles is not None else []

    def has_role_or_is_superuser(self, role: str = None) -> bool:
        """Check if user has role or is superuser."""
        if 'superuser' in self.roles:
            return True
        elif role is not None:
            return role in self.roles
        else:
            return False

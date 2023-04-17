"""Models of the core extension."""
from django.contrib.auth import get_user_model
from simple_history import register

# Create a history for the default user model
register(get_user_model(), app=__package__)

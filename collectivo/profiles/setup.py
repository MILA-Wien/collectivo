"""Setup function for the profiles extension."""
from django.conf import settings
from django.contrib.auth import get_user_model
from collectivo.emails.models import EmailAutomation

from collectivo.extensions.models import Extension
from collectivo.utils.dev import DEV_MEMBERS

from .apps import ProfilesConfig
from .models import ProfileSettings, ProfileSettingsField, UserProfile

User = get_user_model()


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    extension = Extension.objects.register(
        name=ProfilesConfig.name,
        description=ProfilesConfig.description,
        built_in=True,
    )

    # Initialize settings
    ProfileSettings.object()

    # Create default profile fields
    fields = [
        "person_type",
        "gender",
        "birthday",
        "legal_name",
        "legal_form",
        "legal_id",
        "address_street",
        "address_number",
        "address_stair",
        "address_door",
        "address_postcode",
        "address_city",
        "address_country",
        "phone",
    ]
    for field in fields:
        ProfileSettingsField.objects.get_or_create(
            name=field, label=field.capitalize().replace("_", " ")
        )

    # Create missing profiles
    users = User.objects.filter(profile__isnull=True)
    for user in users:
        UserProfile.objects.get_or_create(user=user)
    
    # Create email automations for user creation
    try:
        EmailAutomation.objects.register(
                name="new_user_created",
                label="New user created",
                description=(
                    "A user was created. The user is accesible vie {{ user }} and the profile via {{ profile }}."
                ),
                extension=extension,
                admin_only=False,
            )
    except Exception as e:
        print(e)
    if settings.COLLECTIVO["example_data"] is True:
        for first_name in DEV_MEMBERS:
            email = f"test_{first_name}@example.com"
            user = get_user_model().objects.get(email=email)
            UserProfile.objects.get_or_create(user=user)

"""Fixtures for the tests of the users module."""
from django.urls import reverse

EMAIL = "test_user@example.com"
PASSWORD = "Test123!"
TEST_USER = {
    "first_name": "Test",
    "last_name": "User",
    "email": EMAIL,
}
PUBLIC_URL = reverse("collectivo:collectivo.users:test_view_public")
PRIVATE_URL = reverse("collectivo:collectivo.users:test_view_private")

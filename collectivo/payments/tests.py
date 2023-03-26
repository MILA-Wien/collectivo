"""Tests of the payments extension."""
from django.test import TestCase

from collectivo.utils.test import create_testuser

from .models import PaymentProfile


class ProfileTests(TestCase):
    """Tests of the profiles extension."""

    def setUp(self):
        """Prepare test case."""
        self.user = create_testuser()

    def test_profile_automatically_created(self):
        """Test that a profile is automatically created."""
        self.assertTrue(PaymentProfile.objects.filter(user=self.user).exists())

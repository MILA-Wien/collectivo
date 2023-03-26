"""Tests of the extension."""
from django.test import TestCase

from collectivo.utils.test import create_testuser


class ExtensionTests(TestCase):
    """Tests of the extension."""

    def setUp(self):
        """Prepare test case."""
        self.user = create_testuser()

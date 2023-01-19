"""Models of the devtools app."""
from django.db import models


class TestResource(models.Model):
    """A test resource."""

    name = models.CharField(max_length=255)

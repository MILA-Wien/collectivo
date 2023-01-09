"""Models of the emails module."""
from django.db import models


class EmailTemplate(models.Model):
    """A template of an email."""

    subject = models.CharField(max_length=255)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


class EmailBatch(models.Model):
    """A log of an email batch."""

    email = models.ForeignKey(
        'EmailTemplate', on_delete=models.SET_NULL, null=True)
    sent = models.DateTimeField(auto_now_add=True)
    recipients = models.ManyToManyField('members.Member')

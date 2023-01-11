"""Models of the emails module."""
from django.db import models


class EmailDesign(models.Model):
    """A design of an email."""

    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


class EmailTemplate(models.Model):
    """A template of an email."""

    design = models.ForeignKey(
        'emails.EmailDesign',
        on_delete=models.SET_NULL, null=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


class EmailCampaign(models.Model):
    """A mass email that is being processed or has been sent."""

    # Use a template
    template = models.ForeignKey(
        'emails.EmailTemplate',
        on_delete=models.SET_NULL, null=True)

    # Use a custom subject and message
    design = models.ForeignKey(
        'emails.EmailDesign',
        on_delete=models.SET_NULL, null=True)
    subject = models.CharField(max_length=255, null=True)
    message = models.TextField(null=True)

    status = models.CharField(
        max_length=255, default='working', choices=[
            ('working', 'working'),
            ('success', 'success'),
            ('failure', 'failure')
        ]
    )
    status_message = models.CharField(max_length=255, null=True)
    created = models.DateTimeField(auto_now_add=True)
    recipients = models.ManyToManyField('members.Member')

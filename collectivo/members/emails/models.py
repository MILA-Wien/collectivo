"""Models of the emails module."""
from django.db import models


class EmailDesign(models.Model):
    """A design of an email."""

    name = models.CharField(max_length=255, unique="True")
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the object."""
        return self.name


class EmailTemplate(models.Model):
    """A template of an email."""

    name = models.CharField(max_length=255, unique="True")
    design = models.ForeignKey(
        'emails.EmailDesign',
        on_delete=models.SET_NULL, null=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    tag = models.ForeignKey(
        'members.MemberTag', on_delete=models.SET_NULL, null=True,
        help_text="This tag will be added to recipients if campaign is sent."
    )

    def __str__(self):
        """Return a string representation of the object."""
        return self.name


class EmailCampaign(models.Model):
    """A mass email that is being processed or has been sent."""

    template = models.ForeignKey(
        'emails.EmailTemplate',
        on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=10, default='draft', choices=[
            ('draft', 'draft'),
            ('pending', 'pending'),
            ('success', 'success'),
            ('failure', 'failure')
        ]
    )
    status_message = models.CharField(max_length=255, null=True)
    created = models.DateTimeField(auto_now_add=True)
    sent = models.DateTimeField(null=True)
    recipients = models.ManyToManyField('members.Member')

    def __str__(self):
        """Return a string representation of the object."""
        return "Email campaign "\
            f"({self.id}, {self.status}, {self.template.name})"

"""Models of the emails module."""
from django.contrib.auth import get_user_model
from django.db import models


class EmailDesign(models.Model):
    """A design of an email, which can be applied to a template."""

    name = models.CharField(max_length=255, unique="True")
    body = models.TextField()

    def __str__(self):
        """Return a string representation of the object."""
        return self.name


class EmailTemplate(models.Model):
    """A template of an email, which can be applied to a campaign."""

    name = models.CharField(max_length=255, unique="True")
    design = models.ForeignKey(
        "emails.EmailDesign", on_delete=models.SET_NULL, null=True
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    tag = models.ForeignKey(
        "tags.Tag",
        on_delete=models.SET_NULL,
        null=True,
        help_text="This tag will be added to recipients if campaign is sent.",
    )

    def __str__(self):
        """Return a string representation of the object."""
        return self.name


class EmailCampaign(models.Model):
    """An email campaign that can be used to send mass emails."""

    template = models.ForeignKey(
        "emails.EmailTemplate", on_delete=models.SET_NULL, null=True
    )
    status = models.CharField(
        max_length=10,
        default="draft",
        choices=[
            ("draft", "draft"),
            ("pending", "pending"),
            ("success", "success"),
            ("failure", "failure"),
        ],
    )
    status_message = models.CharField(max_length=255, null=True)
    sent = models.DateTimeField(null=True)
    recipients = models.ManyToManyField(get_user_model())
    extension = models.ForeignKey(
        "extensions.Extension",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The extension that created this campaign.",
    )

    def __str__(self):
        """Return a string representation of the object."""
        return (
            "Email campaign "
            f"({self.id}, {self.status}, {self.template.name})"
        )

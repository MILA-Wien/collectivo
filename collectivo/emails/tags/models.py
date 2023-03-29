"""Models of the emails_tags extension."""
from django.db import models
from django.db.models import signals

from collectivo.emails.models import EmailTemplate


class EmailTemplateTag(models.Model):
    """Mediator between an email template and a tag."""

    template = models.OneToOneField(
        "emails.EmailTemplate",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="tag",
    )
    tag = models.ForeignKey(
        "tags.Tag",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="email_templates",
    )


def create_email_template_tag_connector(sender, instance, created, **kwargs):
    """Create user profile when a user is created."""
    if created:
        EmailTemplateTag.objects.create(template=instance)


signals.post_save.connect(
    create_email_template_tag_connector,
    sender=EmailTemplate,
    dispatch_uid="create_email_template_tag_connector",
    weak=False,
)

"""Models of the emails module."""
from celery import chain
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template import Context, Template
from django.utils import timezone
from html2text import html2text
from simple_history.models import HistoricalRecords

from collectivo.utils.managers import NameManager

from .tasks import send_mails_async, send_mails_async_end


class EmailAutomation(models.Model):
    """An automation that sends emails to users."""

    objects = NameManager()
    history = HistoricalRecords()

    name = models.CharField(max_length=255, unique="True")
    is_active = models.BooleanField(
        default=False,
        verbose_name="Active",
        help_text=(
            "If checked, this automation will be active and send emails."
        ),
    )
    description = models.TextField()
    extension = models.ForeignKey(
        "extensions.Extension",
        on_delete=models.CASCADE,
    )
    admin_only = models.BooleanField(default=False)

    design = models.ForeignKey(
        "emails.EmailDesign",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="automations",
    )
    subject = models.CharField(
        max_length=255,
        blank=True,
    )
    body = models.TextField(
        blank=True,
    )

    admin_design = models.ForeignKey(
        "emails.EmailDesign",
        on_delete=models.PROTECT,
        null=True,
        related_name="automations_admin",
        verbose_name="Design",
    )
    admin_subject = models.CharField(
        max_length=255, verbose_name="Subject", blank=True
    )
    admin_body = models.TextField(verbose_name="Body", blank=True)
    admin_recipients = models.ManyToManyField(
        get_user_model(),
        verbose_name="Recipients",
        related_name="admin_email_automations",
        blank=True,
    )

    def send(self, recipients, context=None):
        """Send emails to recipients."""
        if self.is_active:
            campaign = EmailCampaign.objects.create(
                automation=self,
                extension=self.extension,
            )
            campaign.recipients.set(recipients)
            campaign.save()
            campaign.send(context=context)


class EmailDesign(models.Model):
    """A design of an email, which can be applied to a template."""

    objects = NameManager()
    history = HistoricalRecords()

    name = models.CharField(max_length=255, unique="True")
    body = models.TextField()

    def __str__(self):
        """Return a string representation of the object."""
        return self.name


class EmailTemplate(models.Model):
    """A template of an email, which can be applied to a campaign."""

    objects = NameManager()
    history = HistoricalRecords()

    name = models.CharField(max_length=255, unique="True")
    design = models.ForeignKey(
        "emails.EmailDesign", on_delete=models.PROTECT, null=True
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        """Return a string representation of the object."""
        return self.name


class EmailCampaign(models.Model):
    """An email campaign that can be used to send mass emails."""

    history = HistoricalRecords()

    template = models.ForeignKey(
        "emails.EmailTemplate", on_delete=models.SET_NULL, null=True
    )
    automation = models.ForeignKey(
        "emails.EmailAutomation", on_delete=models.SET_NULL, null=True
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
    recipients = models.ManyToManyField(
        get_user_model(), related_name="emails"
    )
    extension = models.ForeignKey(
        "extensions.Extension",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The extension that created this campaign.",
    )

    def __str__(self):
        """Return a string representation of the object."""
        return f"{self.template.name} ({self.sent})"

    def send(self, context=None):
        """Send emails to recipients."""
        campaign = self
        campaign.sent = timezone.now()
        campaign.status = "pending"
        campaign.save()

        # Generate emails from automation
        if self.automation:
            email_batches = self.create_email_batches(
                self.automation.admin_design,
                self.automation.admin_subject,
                self.automation.admin_body,
                self.automation.admin_recipients.all(),
                context=context,
            )
            if not self.automation.admin_only:
                email_batches += self.create_email_batches(
                    self.automation.design,
                    self.automation.subject,
                    self.automation.body,
                    self.recipients.all(),
                    context=context,
                )

        # Generate emails from template
        else:
            email_batches = self.create_email_batches(
                self.campaign.template.design,
                self.campaign.template.subject,
                self.campaign.template.body,
                self.recipients.all(),
                context=context,
            )

        # Create a chain of async tasks to send emails
        results = {"n_sent": 0, "campaign": self}
        tasks = []
        tasks.append(send_mails_async.s(results, email_batches.pop(0)))
        for email_batch in email_batches:
            tasks.append(send_mails_async.s(email_batch))
        tasks.append(send_mails_async_end.s())
        try:
            chain(*tasks)()
        except Exception as e:
            self.status = "failure"
            self.status_message = str(e)
            self.save()
            raise e

    def create_email_batches(
        self, design, subject, body, recipients, context=None
    ):
        """Create a list of emails, split into batches."""

        if design is not None:
            body = design.body.replace("{{content}}", body)
        from_email = settings.DEFAULT_FROM_EMAIL
        emails = []
        for recipient in recipients:
            body_html = Template(body).render(
                Context({"user": recipient, **(context or {})})
            )
            body_text = html2text(body_html)
            if recipient.email in (None, ""):
                self.status = "failure"
                self.status_message = f"{recipient} has no email."
                self.save()
                raise ValueError(self.status_message)
            email = EmailMultiAlternatives(
                subject, body_text, from_email, [recipient.email]
            )
            email.attach_alternative(body_html, "text/html")
            emails.append(email)

        # Split recipients into batches
        n = 20  # TODO Get this number from the settings
        return [emails[i : i + n] for i in range(0, len(emails), n)]

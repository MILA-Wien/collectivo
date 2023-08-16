"""Models of the emails module."""
from celery import chain
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.db import models
from django.template import Context, Template
from django.utils import timezone
from html2text import html2text
from simple_history.models import HistoricalRecords

from collectivo.utils.managers import NameManager

from .tasks import send_mails_async, send_mails_async_end


class EmailAutomation(models.Model):
    """An automation that sends emails to users."""

    class Meta:
        """Model settings."""

        unique_together = ("name", "extension")

    objects = NameManager()
    history = HistoricalRecords()

    name = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
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

    template = models.ForeignKey(
        "emails.EmailTemplate",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="automations",
    )

    admin_template = models.ForeignKey(
        "emails.EmailTemplate",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="automations_admin",
    )

    admin_recipients = models.ManyToManyField(
        get_user_model(),
        verbose_name="Recipients",
        related_name="admin_email_automations",
        blank=True,
    )

    def send(self, recipients, context=None):
        """Send emails to recipients."""
        if self.is_active:
            # Generate email campaign for admins from automation
            if (self.admin_recipients.exists()):
                admin_campaign = EmailCampaign.objects.create(
                    template=self.admin_template,
                    extension=self.extension,
                )
                admin_campaign.recipients.set(self.admin_recipients.all())
                admin_campaign.save()
                admin_campaign.send(context=context)

            if not self.admin_only:
                # Generate email campaign for end users from automation
                user_campaign = EmailCampaign.objects.create(
                    template=self.template,
                    extension=self.extension,
                )
                user_campaign.recipients.set(recipients)
                user_campaign.save()
                user_campaign.send(context=context)


class EmailSenderConfig(models.Model):
    """The configuration for sending emails (email server config, etc.)."""

    objects = NameManager()
    history = HistoricalRecords()

    name = models.CharField(max_length=255, unique="True")
    from_email = models.CharField(max_length=255, validators=[validate_email])

    host = models.CharField(max_length=255)
    port = models.SmallIntegerField()

    security_protocol = models.CharField(
        max_length=4,
        default="none",
        choices=[
            ("none", "none"),
            ("ssl", "SSL"),
            ("tls", "TLS"),
        ],
    )

    host_user = models.CharField(max_length=255)
    host_password = models.CharField(max_length=255)

    def __str__(self):
        """Return a string representation of the object."""
        return self.name

    def get_backend_config_kwargs(self):
        """Return the email backend config args for this sender config.

        These need to be passed to `core.django.mail.get_connection(**kwargs)`
        """
        return {
            'host': self.host,
            'port': self.port,
            'username': self.host_user,
            'password': self.host_password,
            'use_tls': self.security_protocol == "tls",
            'use_ssl': self.security_protocol == "ssl"}


class EmailDesign(models.Model):
    """A design of an email, which can be applied to a template."""

    objects = NameManager()
    history = HistoricalRecords()

    name = models.CharField(max_length=255, unique="True")
    body = models.TextField()

    def __str__(self):
        """Return a string representation of the object."""
        return self.name

    def apply(self, content):
        """Apply this design to the given content."""
        return self.body.replace("{{content}}", content)


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
    sender_config = models.ForeignKey(
        "emails.EmailSenderConfig", on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        """Return a string representation of the object."""
        return self.name

    def render(self, recipient, context=None):
        """Render the email template for the given recipient."""
        if self.design is not None:
            body_with_design_applied = self.design.apply(self.body)
        else:
            body_with_design_applied = self.body

        if self.sender_config is not None:
            from_email = self.sender_config.from_email
        else:
            from_email = settings.DEFAULT_FROM_EMAIL

        body_html = Template(body_with_design_applied).render(
            Context({"user": recipient, **(context or {})})
        )
        body_text = html2text(body_html)
        email = EmailMultiAlternatives(
            self.subject, body_text, from_email, [recipient.email]
        )
        email.attach_alternative(body_html, "text/html")
        return email


class EmailCampaign(models.Model):
    """An email campaign that can be used to send mass emails."""

    history = HistoricalRecords()

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
        self.sent = timezone.now()
        self.status = "pending"
        self.save()

        # Generate emails from template
        email_batches = self.create_email_batches(context=context)

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

    def create_email_batches(self, context=None):
        """Create a list of emails, split into batches."""
        emails = []
        for recipient in self.recipients.all():
            if recipient.email in (None, ""):
                self.status = "failure"
                self.status_message = f"{recipient} has no email."
                self.save()
                raise ValueError(self.status_message)
            email = self.template.render(recipient, context=context)
            emails.append(email)

        # Split recipients into batches
        n = 20  # TODO Get this number from the settings
        return [emails[i : i + n] for i in range(0, len(emails), n)]

    def get_backend_config_kwargs(self):
        """Return the email backend config args for this sender config.

        These need to be passed to `core.django.mail.get_connection(**kwargs)`
        """
        if self.template.sender_config is not None:
            return self.template.sender_config.get_backend_config_kwargs()
        else:
            # Return the default backend using the values from settings.py
            return {}

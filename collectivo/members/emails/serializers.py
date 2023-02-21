"""Serializers of the emails module."""
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template
from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from . import models
from .tasks import send_mails_async, send_mails_async_end
from html2text import html2text
from celery import chain
from collectivo.members.models import MemberTag
from django.utils import timezone


class EmailDesignSerializer(serializers.ModelSerializer):
    """Serializer for email designs."""

    schema_attrs = {"body": {"input_type": "html"}}

    class Meta:
        """Serializer settings."""

        model = models.EmailDesign
        fields = "__all__"


class EmailTemplateSerializer(serializers.ModelSerializer):
    """Serializer for email templates."""

    schema_attrs = {"body": {"input_type": "html"}}

    class Meta:
        """Serializer settings."""

        model = models.EmailTemplate
        fields = "__all__"


class EmailAutomationSerializer(serializers.ModelSerializer):
    """Serializer for email automations."""

    class Meta:
        """Serializer settings."""

        model = models.EmailAutomation
        fields = "__all__"


class EmailCampaignSerializer(serializers.ModelSerializer):
    """Serializer for email campaigns (email sending orders)."""

    schema_attrs = {"body": {"input_type": "html"}}

    send = serializers.BooleanField(
        write_only=True,
        required=False,
        help_text="Should the campaign be sent now? "
        "Otherwise it will be saved as a draft.",
    )

    class Meta:
        """Serializer settings."""

        model = models.EmailCampaign
        fields = "__all__"
        read_only_fields = (
            "status",
            "status_message",
            "created",
            "sent",
            "automation",
        )

    def validate(self, attrs):
        """Adjust data before validation."""

        # Save send value for later use in view
        self._send = attrs.pop("send", False)

        # Prevent editing of sent campaigns
        if self.instance and self.instance.status != "draft":
            raise ValidationError("Only drafts can be edited.")

        if attrs.get("template") is None:
            raise ValidationError("Template is required.")

        if attrs.get("recipients") is None or attrs.get("recipients") == []:
            raise ValidationError("Recipients are required.")

        # Data together with instance data if objects already exists
        data = self.instance.__dict__ if self.instance else {}
        data.update(attrs)

        # Prevent sending to members with broken emails tag
        recipients = data.get("recipients")
        tag = MemberTag.objects.get_or_create(
            label="Email broken", built_in=True
        )[0]
        if recipients is not None:
            for recipient in recipients:
                if tag in recipient.tags.all():
                    raise ValidationError(
                        f"Recipient {recipient.id} has tag 'broken_email'."
                    )

        return super().validate(attrs)

    def save(self):
        """Save campaign and send emails if requested."""
        super().save()
        if self._send is True:
            self.send_emails()

    def send_emails(self):
        """Send emails to recipients."""
        campaign = self.instance
        campaign.sent = timezone.now()
        campaign.status = "pending"
        campaign.save()

        # Prepare the emails
        template = campaign.template
        recipients = self.validated_data["recipients"]
        subject = template.subject
        body = template.body
        if template.design is not None:
            body = template.design.body.replace("{{content}}", template.body)
        from_email = settings.DEFAULT_FROM_EMAIL
        emails = []
        for recipient in recipients:
            body_html = Template(body).render(Context({"member": recipient}))
            body_text = html2text(body_html)
            email = EmailMultiAlternatives(
                subject, body_text, from_email, [recipient.email]
            )
            email.attach_alternative(body_html, "text/html")
            emails.append(email)

        # Split recipients into batches
        n = 20  # TODO Get this number from the settings
        batches = [emails[i : i + n] for i in range(0, len(emails), n)]

        # Create a chain of async tasks to send the emails
        results = {"n_sent": 0, "campaign": campaign}
        tasks = []
        tasks.append(send_mails_async.s(results, batches.pop(0)))
        for batch in batches:
            tasks.append(send_mails_async.s(batch))
        tasks.append(send_mails_async_end.s())
        try:
            chain(*tasks)()
        except Exception as e:
            campaign.status = 'failure'
            campaign.status_message = str(e)
            campaign.save()
            raise e

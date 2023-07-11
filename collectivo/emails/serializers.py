"""Serializers of the emails module."""
from celery import chain
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template
from django.utils import timezone
from html2text import html2text
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from collectivo.extensions.models import Extension
from collectivo.tags.models import Tag
from collectivo.utils.schema import Schema
from collectivo.utils.serializers import create_history_serializer

from . import models
from .tasks import send_mails_async, send_mails_async_end

User = get_user_model()


class EmailProfileSerializer(serializers.ModelSerializer):
    """Serializer for email profiles."""

    emails = serializers.PrimaryKeyRelatedField(
        many=True, queryset=models.EmailCampaign.objects.all()
    )

    class Meta:
        """Serializer settings."""

        label = "Emails"
        model = User
        fields = ["id", "emails"]
        read_only_fields = ["id", "emails"]


class EmailDesignSerializer(serializers.ModelSerializer):
    """Serializer for email designs."""

    class Meta:
        """Serializer settings."""

        model = models.EmailDesign
        fields = "__all__"


if_not_admin_only = {
    "condition": "equals",
    "value": False,
    "field": "admin_only",
}


class EmailAutomationSerializer(serializers.ModelSerializer):
    """Serializer for email Automations."""

    class Meta:
        """Serializer settings."""

        model = models.EmailAutomation
        exclude = ["name"]
        read_only_fields = ["extension", "description", "name"]
        schema_attrs = {
            "admin_body": {"input_type": "html"},
            "admin_only": {"visible": False},
            "subject": {"visible": if_not_admin_only},
            "body": {"input_type": "html", "visible": if_not_admin_only},
            "design": {"visible": if_not_admin_only},
        }
        schema: Schema = {
            "actions": ["list", "retrieve", "update"],
            "structure": [
                {
                    "fields": ["label", "extension", "description"],
                    "style": "read_only",
                },
                {
                    "label": "General settings",
                    "fields": ["is_active"],
                },
                {
                    "label": "Email to users",
                    "description": "This template will be sent to users.",
                },
                {"fields": ["subject", "design"], "style": "row"},
                {"fields": ["body"]},
                {
                    "label": "Email to admins",
                    "description": "This template will be sent to admins.",
                },
                {
                    "fields": [
                        "admin_subject",
                        "admin_design",
                        "admin_recipients",
                    ],
                    "style": "row",
                },
                {
                    "fields": [
                        "admin_body",
                    ],
                },
            ],
        }


class EmailTemplateSerializer(serializers.ModelSerializer):
    """Serializer for email templates."""

    tag__tag = serializers.PrimaryKeyRelatedField(
        source="tag.tag",
        queryset=Tag.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        """Serializer settings."""

        model = models.EmailTemplate
        fields = "__all__"
        schema_attrs = {"body": {"input_type": "html"}}

    def create(self, validated_data):
        """Create a new template."""
        if "tag" not in validated_data:
            return super().create(validated_data)

        tag = validated_data.pop("tag")["tag"]
        obj = super().create(validated_data)
        obj.tag.tag = tag
        obj.tag.save()
        return obj

    def update(self, instance, validated_data):
        """Update an existing template."""
        if "tag" not in validated_data:
            return super().create(validated_data)

        tag = validated_data.pop("tag")["tag"]
        obj = super().update(instance, validated_data)
        obj.tag.tag = tag
        obj.tag.save()
        return obj


class EmailCampaignSerializer(serializers.ModelSerializer):
    """Serializer for email campaigns (email sending orders)."""

    schema_attrs = {"body": {"input_type": "html"}}

    send = serializers.BooleanField(
        write_only=True,
        required=False,
        help_text=(
            "Should the campaign be sent now? "
            "Otherwise it will be saved as a draft."
        ),
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
            "extension",
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
        extension = Extension.objects.get(name="emails")
        tag = Tag.objects.get_or_create(
            name="Email broken", extension=extension
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
            body_html = Template(body).render(Context({"user": recipient}))
            body_text = html2text(body_html)
            if recipient.email in (None, ""):
                campaign.status = "failure"
                campaign.status_message = f"{recipient} has no email."
                campaign.save()
                raise ValueError(campaign.status_message)
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
            campaign.status = "failure"
            campaign.status_message = str(e)
            campaign.save()
            raise e


EmailCampaignHistorySerializer = create_history_serializer(
    models.EmailCampaign
)
EmailTemplateHistorySerializer = create_history_serializer(
    models.EmailTemplate
)
EmailAutomationHistorySerializer = create_history_serializer(
    models.EmailAutomation
)
EmailDesignHistorySerializer = create_history_serializer(models.EmailDesign)

"""Views of the emails module."""
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template
from django.conf import settings
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from collectivo.members.permissions import IsMembersAdmin
from . import models, serializers
from .tasks import send_mails_async, send_mails_async_end
from html2text import html2text
from celery import chain


class EmailDesignViewSet(viewsets.ModelViewSet):
    """Manage email designs."""

    permission_classes = [IsMembersAdmin]
    serializer_class = serializers.EmailDesignSerializer
    queryset = models.EmailDesign.objects.all()


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """Manage email templates."""

    permission_classes = [IsMembersAdmin]
    serializer_class = serializers.EmailTemplateSerializer
    queryset = models.EmailTemplate.objects.all()


class EmailCampaignViewSet(viewsets.ModelViewSet):
    """Manage email campaigns (mass email orders)."""

    permission_classes = [IsMembersAdmin]
    serializer_class = serializers.EmailCampaignSerializer
    queryset = models.EmailCampaign.objects.all()

    def perform_create(self, serializer):
        """Send the emails."""
        direct_data = [serializer.validated_data.get(x)
                       for x in ['subject', 'message', 'design']]
        if serializer.validated_data.get('template'):
            if direct_data != [None, None, None]:
                raise ValidationError("Cannot use template together with "
                                      "subject, message, or design.")
        else:
            if None in direct_data:
                raise ValidationError("Must specify subject, message, "
                                      "and design if no template is used.")

        # Save instance if there are no validation errors
        serializer.save()
        campaign = serializer.instance

        # Apply template (overrides other data)
        if campaign.template is not None:
            campaign.subject = campaign.template.subject
            campaign.message = campaign.template.message
            campaign.design = campaign.template.design

        # Apply design
        if campaign.design is not None:
            campaign.message = campaign.design.body\
                .replace('{{content}}', campaign.message)
            campaign.save()

        # Prepare the emails
        recipients = serializer.validated_data['recipients']
        subject = campaign.subject
        message = campaign.message
        from_email = settings.DEFAULT_FROM_EMAIL
        emails = []
        for recipient in recipients:
            body_html = Template(message)\
                .render(Context({'member': recipient}))
            body_text = html2text(body_html)
            email = EmailMultiAlternatives(
                subject, body_text, from_email, [recipient.email])
            email.attach_alternative(body_html, "text/html")
            emails.append(email)

        # Split recipients into batches
        n = 100  # TODO Get this number from the settings
        batches = [emails[i:i+n] for i in range(0, len(emails), n)]

        # Create a chain of async tasks to send the emails
        results = {'n_sent': 0, 'campaign': campaign}
        tasks = []
        tasks.append(send_mails_async.s(results, batches.pop(0)))
        for batch in batches:
            tasks.append(send_mails_async.s(batch))
        tasks.append(send_mails_async_end.s())
        chain(*tasks)()

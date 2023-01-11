"""Views of the emails module."""
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template
from django.conf import settings
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from collectivo.auth.permissions import IsSuperuser
from . import models, serializers
from .tasks import send_mails_async, send_mails_async_end
from html2text import html2text
from celery import chain


class EmailDesignViewSet(viewsets.ModelViewSet):
    """Manage email designs."""

    permission_classes = [IsSuperuser]
    serializer_class = serializers.EmailDesignSerializer
    queryset = models.EmailDesign.objects.all()


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """Manage email templates."""

    permission_classes = [IsSuperuser]
    serializer_class = serializers.EmailTemplateSerializer
    queryset = models.EmailTemplate.objects.all()


class EmailBatchViewSet(viewsets.ModelViewSet):
    """Send mass emails and manage logs."""

    permission_classes = [IsSuperuser]
    serializer_class = serializers.EmailBatchSerializer
    queryset = models.EmailBatch.objects.all()

    def send_bulk_email(self, model, recipients, subject, message, from_email):
        """Send an html email to a list of recipients."""
        emails = []
        for recipient in recipients:
            body_html = Template(message)\
                .render(Context({'member': recipient}))
            body_text = html2text(body_html)
            email = EmailMultiAlternatives(
                subject, body_text, from_email, [recipient.email])
            email.attach_alternative(body_html, "text/html")
            emails.append(email)

        # Split emails into batches of size 100
        batches = [emails[i:i+100] for i in range(0, len(emails), 100)]

        # Create a chain of async tasks to send the emails
        results = {'n_sent': 0}
        tasks = []
        tasks.append(send_mails_async.s(results, batches.pop(0)))
        for batch in batches:
            tasks.append(send_mails_async.s(batch))
        tasks.append(send_mails_async_end.s(model))
        chain(*tasks)()

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
        batch = serializer.instance

        # Apply template (overrides other data)
        if batch.template is not None:
            batch.subject = batch.template.subject
            batch.message = batch.template.message
            batch.design = batch.template.design

        # Apply design
        if batch.design is not None:
            batch.message = batch.design.body\
                .replace('{{content}}', batch.message)
            batch.save()

        # Send emails in background
        self.send_bulk_email(
            model=batch,
            recipients=serializer.validated_data['recipients'],
            subject=batch.subject, message=batch.message,
            from_email=settings.DEFAULT_FROM_EMAIL
        )

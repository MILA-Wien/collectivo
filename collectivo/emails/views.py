"""Views of the emails module."""
from django.core.mail import EmailMultiAlternatives
from django.core import mail
from django.template import Context, Template
from rest_framework import viewsets
from collectivo.auth.permissions import IsSuperuser
from . import models, serializers
from html2text import html2text


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

    def send_bulk_email(self, recipients, subject, message, from_email):
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
        connection = mail.get_connection()
        return connection.send_messages(emails)

    def perform_create(self, serializer):
        """Send the emails."""
        serializer.save()
        batch = serializer.instance

        # Apply template
        if batch.template is not None:
            batch.subject = batch.template.subject
            batch.message = batch.template.message
            batch.design = batch.template.design

        # Apply design
        if batch.design is not None:
            batch.message = batch.design.body\
                .replace('{{content}}', batch.message)
            batch.save()

        # Try to send emails (TODO Do this as a background task)
        n_success = self.send_bulk_email(
            recipients=serializer.validated_data['recipients'],
            subject=batch.subject, message=batch.message,
            from_email='mitmachen@mila.wien'
        )

        # Log success
        if n_success != len(serializer.validated_data['recipients']):
            serializer.instance.status = 'failed'
        else:
            serializer.instance.status = 'success'
        serializer.instance.save()

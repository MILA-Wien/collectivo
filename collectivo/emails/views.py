"""Views of the emails module."""
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.core import mail
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from collectivo.auth.permissions import IsSuperuser
from . import models, serializers
import time


def send_bulk_email(recipients, subject, message, from_email):
    """Send an html email to a list of recipients."""
    emails = []
    for recipient in recipients:
        html_content = message
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(
            subject, text_content, from_email, [recipient])
        email.attach_alternative(html_content, "text/html")
        emails.append(email)
    connection = mail.get_connection()
    return connection.send_messages(emails)


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

    def perform_create(self, serializer):
        """Send the emails."""
        serializer.save()
        n_success = send_bulk_email(
            recipients=serializer.validated_data['recipients'],
            subject=serializer.validated_data['template'].subject,
            message=serializer.validated_data['template'].message,
            from_email='mitmachen@mila.wien'
        )
        #  time.sleep(5) TODO Background task
        if n_success != len(serializer.validated_data['recipients']):
            serializer.instance.status = 'failed'
        else:
            serializer.instance.status = 'success'
        serializer.instance.save()

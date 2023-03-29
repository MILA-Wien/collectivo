"""Celery tasks of the emails module."""
import time

from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.core import mail

from collectivo.emails.models import EmailCampaign

logger = get_task_logger(__name__)
User = get_user_model()


@shared_task
def send_mails_async(results, emails):
    """Send a mass email."""
    connection = mail.get_connection()
    campaign = results["campaign"]

    try:
        time.sleep(1)  # TODO Get this number from the settings
        results["n_sent"] += connection.send_messages(emails)
    except Exception as e:
        campaign.status = "failure"
        campaign.status_message = str(e)
        campaign.save()
        logger.error("Error sending emails: %s", e)
        # TODO Send an email to the admins

    # Add optional tag to recipients if batch is successful
    # TODO: Make tag optional for loose coupling
    if campaign.template.tag.tag is not None:
        for email in emails:
            user = User.objects.get(email=email.to[0])
            tag = campaign.template.tag.tag
            tag.refresh_from_db()
            tag.users.add(user)
            tag.save()

    return results


@shared_task
def send_mails_async_end(results):
    """Document results of sending emails in the database."""
    campaign = results["campaign"]
    campaign = EmailCampaign.objects.get(id=campaign.id)  # Refresh from DB
    if results["n_sent"] != campaign.recipients.count():
        campaign.status = "failure"
        campaign.status_message = (
            "Not all emails were sent"
            f'({results["n_sent"]}/{campaign.recipients.count()})'
        )
        # TODO Send an email to the admins
    else:
        campaign.status = "success"
    campaign.save()

"""Celery tasks of the emails module."""
from celery import shared_task
from django.core import mail
from celery.utils.log import get_task_logger
import time
from smtplib import SMTPException


logger = get_task_logger(__name__)


@shared_task
def send_mails_async(results, emails):
    """Send a mass email."""
    connection = mail.get_connection()
    try:
        results['n_sent'] += connection.send_messages(emails)
    except SMTPException as e:
        campaign = results['campaign']
        campaign.status = 'failure'
        campaign.status_message = str(e)
        campaign.save()
        # TODO Send an email to the admins
        raise e
    # TODO Get this number from the settings
    time.sleep(1)
    return results


@shared_task
def send_mails_async_end(results):
    """Document results of sending emails in the database."""
    campaign = results['campaign']
    if results['n_sent'] != campaign.recipients.count():
        campaign.status = 'failure'
        campaign.status_message = 'Not all emails were sent' \
            f'({results["n_sent"]}/{campaign.recipients.count()})'
        # TODO Send an email to the admins
    else:
        campaign.status = 'success'
    campaign.save()

"""Celery tasks of the emails module."""
from celery import shared_task
from django.core import mail
import logging


logger = logging.getLogger(__name__)


@shared_task
def send_mails_async(results, emails):
    """Send a batch of emails."""
    logger.info("Starting to send mails")
    connection = mail.get_connection()
    results['n_sent'] += connection.send_messages(emails)
    logger.info("SEND MAILS: " + str(results))

    return results


@shared_task
def send_mails_async_end(results):
    """Document results of sending emails in the database."""
    logger.info("REACHED THE END OF SENDING MAILS: " + str(results))
    # TODO Log success in database

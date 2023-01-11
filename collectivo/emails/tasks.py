"""Celery tasks of the emails module."""
from celery import shared_task
from django.core import mail
from celery.utils.log import get_task_logger
import time

logger = get_task_logger(__name__)


@shared_task
def send_mails_async(results, emails):
    """Send a batch of emails."""
    connection = mail.get_connection()
    results['n_sent'] += connection.send_messages(emails)
    time.sleep(1)
    return results


@shared_task
def send_mails_async_end(results, model):
    """Document results of sending emails in the database."""
    model.n_sent = results['n_sent']
    model.status = 'success'
    model.save()

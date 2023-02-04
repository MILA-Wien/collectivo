"""Celery tasks for collectivo_app."""

from celery import shared_task
import ping3


@shared_task(name="ping")
def ping():
    """Ping Test if the server is up."""
    try:
        ping3.ping("collectivo")
        print("Success")
    except Exception as e:
        print("Task ping collectivo failed with {}".format(e))
        # Todo Send an email to the admins -> should we use the email module?

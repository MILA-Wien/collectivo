"""Celery tasks of the lotzapp extension."""
from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model

from collectivo.utils.tasks import LogErrorRetryTask

from . import models

User = get_user_model()
logger = get_task_logger(__name__)


@shared_task(base=LogErrorRetryTask)
def sync_lotzapp_invoice(invoice):
    """Sync a lotzapp invoice."""
    try:
        models.LotzappInvoice.objects.get_or_create(invoice=invoice)[0].sync()
    except Exception as e:
        logger.error(f"Lotzapp sync failed: {e}", exc_info=True)
        return e


@shared_task(base=LogErrorRetryTask)
def sync_lotzapp_user(user):
    """Sync a lotzapp address."""
    try:
        models.LotzappAddress.objects.get_or_create(user=user)[0].sync()
    except Exception as e:
        logger.error(f"Lotzapp sync failed: {e}", exc_info=True)
        return e


@shared_task(base=LogErrorRetryTask)
def sync_lotzapp_end(results, log: models.LotzappSync):
    """Finish lotzapp sync action."""
    log.refresh_from_db()
    n = len(results)
    errors = [r for r in results if isinstance(r, Exception)]
    if errors:
        log.status = "failure"
        log.status_message = f"{n-len(errors)}/{n} {log.type} synced"
        log.save()
        return
    log.status = "success"
    log.status_message = f"{n}/{n} {log.type} synced"
    log.save()

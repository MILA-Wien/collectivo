"""Collectivo utility functions for Celery tasks."""
from celery import Task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class LogErrorTask(Task):
    """A celery tasks that logs exceptions."""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log the exception."""
        logger.error(exc, exc_info=True)


class LogErrorRetryTask(LogErrorTask):
    """A celery tasks that logs exceptions and retries automatically."""

    autoretry_for = ((Exception,),)
    max_retries = 5
    retry_backoff = True
    retry_backoff_max = 700
    retry_jitter = False

"""Celery configuration module."""
import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collectivo_app.settings')

app = Celery('collectivo_app')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Add the schedueled tasks to the Celery Beat
# Todo: Add the tasks to the database or how to add tasks from modules?

app.conf.beat_schedule = {
    # Execute the Ping Test every 1 minutes
    'ping-1min': {
        'task': 'ping',
        'schedule': crontab(minute='*/1'),
    },
}

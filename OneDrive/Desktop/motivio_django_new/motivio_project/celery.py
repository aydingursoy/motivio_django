import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motivio_project.settings')

app = Celery('motivio')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Define periodic tasks
app.conf.beat_schedule = {
    'check-maintenance-reminders-daily': {
        'task': 'maintenance.tasks.check_maintenance_reminders',
        'schedule': crontab(hour=8, minute=0),  # Run daily at 8:00 AM
    },
}

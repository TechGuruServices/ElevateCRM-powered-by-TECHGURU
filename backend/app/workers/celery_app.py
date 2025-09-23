"""
Celery application for background tasks
"""
from celery import Celery
import os

# Set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

# You can read the broker URL from environment variables
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/1')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/2')

celery_app = Celery(
    'elevatecrm_worker',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['app.workers.ai_tasks']  # Add your task modules here
)

# Optional configuration, see the Celery documentation for more options:
# https://docs.celeryq.dev/en/stable/userguide/configuration.html
celery_app.conf.update(
    task_track_started=True,
    broker_connection_retry_on_startup=True,
    timezone='UTC',
    enable_utc=True,
)

if __name__ == '__main__':
    celery_app.start()

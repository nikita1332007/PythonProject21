from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

from myproject.project.settings import CELERY_TIMEZONE

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_schedule = {
    'block-inactive-users-every-day': {
        'task': 'lms.tasks.block_inactive_users',
        'schedule': crontab(hour=0, minute=0),  # каждый день в 00:00
    },
}
app.conf.timezone = CELERY_TIMEZONE
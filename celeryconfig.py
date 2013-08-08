from celery import Celery
from celery.schedules import crontab
CELERYBEAT_SCHEDULE = {
    'every-minute': {
        'task': 'tasks.process',
        'schedule': crontab(minute='*/1'),
        'args': None,
    },
}

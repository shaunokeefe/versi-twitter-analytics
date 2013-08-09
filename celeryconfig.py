from celery import Celery
from celery.schedules import crontab
CELERYBEAT_SCHEDULE = {
    'tweets': {
        'task': 'tasks.process_tweets',
        'schedule': crontab(minute='*/1'),
        'args': None,
    },
    'users': {
        'task': 'tasks.process_users',
        'schedule': crontab(minute='*/1'),
        'args': None,
    },
}

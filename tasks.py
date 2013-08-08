from celery import Celery
from get_my_tweets import TweetCollection


celery = Celery('tasks', backend='amqp', broker='amqp://')
celery.config_from_object('celeryconfig')

tweet_collection = TweetCollection()

@celery.task
def process():
    tweet_collection.process(num=200)

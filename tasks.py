from celery import Celery
from get_my_tweets import TweetCollection, UserCollection


celery = Celery('tasks', backend='amqp', broker='amqp://')
celery.config_from_object('celeryconfig')

tweet_collection = TweetCollection()
user_collection = UserCollection()

@celery.task
def process_tweets():
    tweet_collection.process(num=200)

@celery.task
def process_users():
    user_collection.process(num=200)

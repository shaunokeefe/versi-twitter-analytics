import twitter
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from settings import SETTINGS

api = twitter.Api(consumer_key=SETTINGS['CONSUMER_KEY'],
        consumer_secret=SETTINGS['CONSUMER_SECRET'],
        access_token_key=SETTINGS['ACCESS_TOKEN_KEY'],
        access_token_secret=SETTINGS['ACCESS_TOKEN_SECRET'])

db_name = 'twitter_db'

class Collection(object):
    def __init__(self, db_name='collection_db', collection_name='collection_collection'):
        self.oldest_id = None
        self.newest_id = None
        self.has_reached_bottom = False
        self.db_client = MongoClient()
        self.db = self.db_client[db_name]
        self.collection = self.db[collection_name]

    def set_oldest(self, id):
        self.oldest_id = id

    def set_newest(self, id):
        self.newest_id = id

    def clean_to_dict(self, item):
        item_dict = item.AsDict()
        item_dict['_id'] = tweet_dict['id']
        for key in ['urls', 'retweeted_status']:
            try:
                item_dict.pop(key)
            except:
                pass

    def save(self, items):
        for item in items:
            item_dict = clean_to_dict(item)
            try:
       	        id = self.collection.insert(item_dict)
            except DuplicateKeyError:
                pass
        newest =items[0]
        oldest =items[-1]

        if newest.id > self.newest_id or self.newest_id is None:
            self.set_newest(newest.id)
        if oldest.id < self.oldest_id or self.oldest_id is None:
            self.set_oldest(oldest.id)

    def process(self, num=200):
        if not self.has_reached_bottom:
            items = self.get_older(num=num)
            if not items:
                self.has_reached_bottom = True
                return
        else:
            return
            items = self.get_newer(num=num)
        self.save(items)

    def get_newer(self, num=200):
        user_tweets = api.GetUserTimeline(screen_name=SETTINGS['ACCOUNT_DISPLAY_NAME'], since_id=self.newest_id, count=num)
        return user_tweets

    def get_older(self, num=200):
        kwargs = {'count': num, 'screen_name': SETTINGS['ACCOUNT_DISPLAY_NAME']}
        if self.oldest_id:
            kwargs['max_id'] = self.oldest_id - 1
        user_tweets = api.GetUserTimeline(**kwargs)
        return user_tweets

class TweetCollection(Collection):
    def __init__(self, db_name='tweet_db', collection_name='tweet_collection'):
        self.oldest_id = None
        self.newest_id = None
        self.has_reached_bottom = False
        self.db_client = MongoClient()
        self.db = self.db_client[db_name]
        self.collection = self.db[collection_name]

    def set_oldest(self, id):
        self.oldest_id = id

    def set_newest(self, id):
        self.newest_id = id

    def save(self, tweets):
        for tweet in tweets:
            tweet_dict = tweet.AsDict()
            tweet_dict['_id'] = tweet_dict['id']
            for key in ['urls', 'retweeted_status']:
                try:
                    tweet_dict.pop(key)
                except:
                    pass
            try:
       	        id = self.collection.insert(tweet_dict)
            except DuplicateKeyError:
                pass
        newest =tweets[0]
        oldest =tweets[-1]

        if newest.id > self.newest_id or self.newest_id is None:
            self.set_newest(newest.id)
        if oldest.id < self.oldest_id or self.oldest_id is None:
            self.set_oldest(oldest.id)

    def process(self, num=200):
        if not self.has_reached_bottom:
            tweets = self.get_older(num=num)
            if not tweets:
                self.has_reached_bottom = True
                return
        else:
            return
            tweets = self.get_newer(num=num)
        self.save(tweets)

    def get_newer(self, num=200):
        user_tweets = api.GetUserTimeline(screen_name=SETTINGS['ACCOUNT_DISPLAY_NAME'], since_id=self.newest_id, count=num)
        return user_tweets

    def get_older(self, num=200):
        kwargs = {'count': num, 'screen_name': SETTINGS['ACCOUNT_DISPLAY_NAME']}
        if self.oldest_id:
            kwargs['max_id'] = self.oldest_id - 1
        user_tweets = api.GetUserTimeline(**kwargs)
        return user_tweets

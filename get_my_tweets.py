import twitter
from geopy import geocoders
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
        self.backfill = True
        self.db_client = MongoClient()
        self.db = self.db_client[db_name]
        self.collection = self.db[collection_name]
        self.id_field_name = 'id'
        self.add_list = []
        self.item_cache = []

    def set_oldest(self, id):
        self.oldest_id = id

    def set_newest(self, id):
        self.newest_id = id

    def clean_to_dict(self, item):
        item_dict = item.AsDict()
        item_dict_cleaned = {}
        item_dict_cleaned['_id'] = item_dict[self.id_field_name]
        for key in self.add_list:
            item_dict_cleaned[key] = item_dict.get(key, None)

        return item_dict_cleaned

    def add_extra_fields(self, item):
        return item

    def fetch(self, num=200):
        if self.backfill:
            self.item_cache.extend(self.get_older(num=num))
            if not self.item_cache:
                self.backfill = False
                return
        else:
            self.item_cache.extend(self.get_newer(num=num))

        if not self.item_cache == []:
            newest = self.item_cache[0]
            oldest = self.item_cache[-1]

            if newest.id > self.newest_id or self.newest_id is None:
                self.set_newest(newest.id)
            if oldest.id < self.oldest_id or self.oldest_id is None:
                self.set_oldest(oldest.id)

    def has_items(self):
        return not self.item_cache == []

    def save_item(self, item):
        item_dict = self.clean_to_dict(item)
        item_dict = self.add_extra_fields(item_dict)
        try:
            id = self.collection.insert(item_dict)
        except DuplicateKeyError:
            pass

    def save_items(self):
        failed = []

        while self.item_cache:
            try:
                item = self.item_cache.pop()
                self.save_item(item)
            except:
                failed.extend(item)
        self.item_cache = failed

    def process(self, num=200):
        self.fetch(num=num)

        if self.has_items():
            self.save_items()

    def get_newer(self, num=200):
        raise NotImplementedError()

    def get_older(self, num=200):
        raise NotImplementedError()

class TweetCollection(Collection):
    def __init__(self, db_name='tweet_db', collection_name='tweet_collection'):
        super(TweetCollection, self ).__init__(db_name=db_name, collection_name=collection_name)
        self.add_list = ['name', 'text']
        self.id_field_name = 'id'

    def get_newer(self, num=200):
        try:
            user_tweets = api.GetUserTimeline(screen_name=SETTINGS['ACCOUNT_DISPLAY_NAME'])
        except:
            return []
        return user_tweets

    def get_older(self, num=200):
        kwargs = {'count': num, 'screen_name': SETTINGS['ACCOUNT_DISPLAY_NAME']}
        if self.oldest_id:
            kwargs['max_id'] = self.oldest_id - 1
        try:
            user_tweets = api.GetUserTimeline(screen_name=SETTINGS['ACCOUNT_DISPLAY_NAME'])
        except:
            return []
        return user_tweets

class UserCollection(Collection):

    def __init__(self, db_name='tweet_db', collection_name='user_collection'):
        super(UserCollection, self).__init__(db_name=db_name, collection_name=collection_name)
        self.add_list = ['followers_count', 'location', 'name', 'screen_name', 'created_at', 'time_zone']
        self.id_field_name = 'id'
        self.backfill = False

    def add_extra_fields(self, item):
        item = super(UserCollection, self).add_extra_fields(item)
        if item.get('location', False):
            g = geocoders.GoogleV3()
            try:
                geocodes = g.geocode(item['location'], exactly_one = False)
                for geocode in geocodes:
                    place, (lat, lon) = geocode
                    item['latitude'] = lat
                    item['longitude'] = lon
            except:
                # Probably just some lame riddle ('Everywhere. lol!') so give up
                pass
        return item

    def get_newer(self, num=200):
        kwargs = {'skip_status':True}
        try:
            followers = api.GetFollowers(**kwargs)
        except:
            return []
        return followers

    def get_older(self, num=200):
        pass

def get_rate_limit():
    return api.GetRateLimitStatus()

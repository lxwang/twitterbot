import tokens
import tweepy
import asyncio
import csv
import json
import time
import re

follow_file = 'follows.json'

must_follows = ['zerohedge']

default_follows = ['CitronResearch', 'muddywatersre', 'Trinhnomics' 'BNONews', 'DeItaone', 'onlyyoontv', 'elonmusk', 'Newsquawk', 'SqueezeMetrics', 'spotgamma', 'WallStJesus',
         'CryptoPanicCom', 'pakpakchicken', 'Trade_The_News', 'disclosetv', '_lakai_', 'hoodietrades',  'zerohedge',  'LiveSquawk',  'FirstSquawk']

news_list = ['disclosetv', 'zerohedge', 'DeItaone']

follow_list = default_follows
try:
    with open(follow_file) as f:
        follow_list = json.load(f)
except FileNotFoundError:
    print("Twitter follow file not found")
    with open(follow_file, 'w') as file:
        json.dump(default_follows, file)
        print("list updated")

tweet_queue = []

def get_tweet():
    if tweet_queue:
        return tweet_queue.pop(0)
    else:
        return False

def get_user_ids(follow):
    out = api.lookup_users(screen_names=follow, include_entities=False)
    return [x._json['id_str'] for x in out]

def addfollow(acct):
    if not (acct in follow_list):
        follow_list.append(acct)
        update_follows(follow_list)
        return True
    else:
        return False

def unfollow(acct):
    if (acct in follow_list) and (acct not in must_follows):
        follow_list.remove(acct)
        update_follows(follow_list)
        return True
    else:
        return False

def update_follows(f):
    with open(follow_file, 'w') as file:
        json.dump(f, file)
        print("list updated")

    global followed_ids
    followed_ids = get_user_ids(f)
    if stream.running:
        stream.disconnect()
    #stream.filter(follow=followed_ids, is_async=True)



class StreamListener(tweepy.StreamListener):
    def __init__(self):
        super().__init__()
        # remember the content of the last tweet so that we don't double post
        self.last_tweet = ""
    
    def on_status(self, status):
                
        if status.retweeted:
            return
        # don't post out of context replies
        if status.in_reply_to_status_id:
            return

        description = status.user.description
        loc = status.user.location
        text = status.text
        coords = status.coordinates

        name = status.user.screen_name
        user_created = status.user.created_at
        followers = status.user.followers_count
        id_str = status.id_str
        created = status.created_at
        retweets = status.retweet_count


        creator_id = status.user.id_str

        if status.user.screen_name.upper() in map(str.upper, follow_list):
            # filter out retweets unless it's from a news source
            if hasattr(status, 'retweeted_status'):
                print("rt from", status.user.screen_name )
                if not(status.user.screen_name.upper() in map(str.upper, news_list)):
                    return

                # filter out retweets that tweet other accounts being followed
                regex = r"RT @([^:]+):"
                matches = re.findall(regex, status.text, re.MULTILINE)
                if matches[0].upper() in map(str.upper, follow_list):
                    print('filtered out retweet to', matches[0])
                    return
        
            print('{}: {} {}'.format(status.user.screen_name, text, status.source_url))
            tweet_url = 'https://twitter.com/{}/status/{}'.format(status.user.screen_name, status.id_str)
            if len(tweet_queue) == 0 or (not (tweet_url in tweet_queue)):
                if text.strip() == self.last_tweet.strip():
                    print("Double tweet by", status.user.screen_name)
                else:
                    tweet_queue.append(tweet_url)
                    self.last_tweet = text
            print("QUEUE: ", tweet_queue)

    def on_error(self, status_code):
        if status_code == 420:
            print("Twitter stream disconnected.")
            #returning False in on_data disconnects the stream
            return False


async def start_stream():
    while True:
        if stream.running:
            pass
        else:
            stream.filter(follow=followed_ids, is_async=True)
            print("Streaming data from Twitter")
        await asyncio.sleep(10)

auth = tweepy.OAuthHandler(tokens.TWITTER_API_KEY, tokens.TWITTER_API_SECRET)
auth.set_access_token(tokens.ACCESS_KEY, tokens.ACCESS_SECRET)
api = tweepy.API(auth)

followed_ids = get_user_ids(follow_list)

stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)


# start_stream()




# Copyright (c) Paul Tagliamonte, 2012, under the terms of dput-ng.

import twitter
import json
import os

def tweet(changes, profile, interface):
    tweet = "I've just uploaded %s/%s to %s #debian" % (
        changes['Source'],
        changes['Version'],
        profile['name']
    )
    if len(tweet) > 140:
        tweet = tweet[:140]

    obj = json.load(open(os.path.expanduser("~/.twitter.json"), 'r'))
    t = twitter.Api(
        consumer_key=obj['consumer_key'],
        consumer_secret=obj['consumer_secret'],
        access_token_key=obj['oath_token'],
        access_token_secret=obj['oath_secret']
    )

    t.PostUpdates(tweet)

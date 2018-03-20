#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 19:40:46 2018

@author: TrishiaAni
"""

import nltk
nltk.download()

##IMPORTS
import tweepy
import json


##SET UP TWITTER
with open('/path/to/your/twitter_auth.json') as f:
    keys = json.load(f)
        
## Or On Windows ##
#with open (r'C:\Users\username\path_to\twitter_auth.json')
#        keys = json.load(f)
    
consumer_key = keys['consumer_key']
consumer_secret = keys['consumer_secret']
access_token = keys['access_token']
access_token_secret = keys['access_token_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
'''
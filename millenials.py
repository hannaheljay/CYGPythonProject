#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 19:40:46 2018

@author: TrishiaAni
"""


#import nltk
#nltk.download()

##IMPORTS
import tweepy
import json


##SET UP TWITTER
consumer_key = 'eA1I7iyAnxJQr9hwywIbUWElr'
consumer_secret = 'bHSemeLupbySTo0q5MiPqeNLTLjYkIudcLvVQsMNyFF63zEIiJ'
access_token = '838879635752505345-LwopDdzkRhmhYGc10OLXSqpGTyAUi5i'
access_token_secret = '4kyfE2ZuAQI3EBKvUtgiZf358hNSe0XPMsBxrJovkeq33'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


tweets = []

##TWITTER STREAM
class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        tweets.append(status.text.rstrip())
        if len(tweets) > 200:
            myStream.disconnect()

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)


myStream.filter(track=["avocado"], languages=['en'])

##EMOJI DATA
pos_emojis = ['😙','❤','😍','💓','😗','☺','😊','😛','💕','😀','😃','😚']
neg_emojis = ['☹','😕','😩','😒','😠','😐','😦','😣','😫','😖','😞','💔','😢','😟']
all_emojis = pos_emojis + neg_emojis

##FETCH SOME TWEETS
myStream.filter(track=all_emojis, languages=['en'])

def store_tweets(file, tweets):
	with open('tweets.txt', 'r') as f:
		old_tweets = f.readlines()

	all_tweets = old_tweets + tweets
	all_tweets = list(set(all_tweets))
	all_tweets = [tweet.replace('\n',' ')+"\n" for tweet in all_tweets]

	with open('tweets.txt', 'a') as f:
		f.writelines(all_tweets)

	return all_tweets

#STORE THE TWEETS IN TWEETS.TXT. EACH TIME PROGRAM IS RUN, WILL ADD TO THIS FILE
tweets = store_tweets('tweets.txt', tweets)



## i can't get it to save the tweets into the tweets.txt file properly??
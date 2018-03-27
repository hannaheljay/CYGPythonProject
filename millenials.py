#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 19:40:46 2018

@author: TrishiaAni
"""

#import nltk
#nltk.download()


## -------- IMPORTS ---------
import tweepy
import re
import string
import os.path
import nltk.classify.util

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.classify import NaiveBayesClassifier
## --------------------------


## ----- SET UP TWITTER -----
consumer_key = 'eA1I7iyAnxJQr9hwywIbUWElr'
consumer_secret = 'bHSemeLupbySTo0q5MiPqeNLTLjYkIudcLvVQsMNyFF63zEIiJ'
access_token = '838879635752505345-LwopDdzkRhmhYGc10OLXSqpGTyAUi5i'
access_token_secret = '4kyfE2ZuAQI3EBKvUtgiZf358hNSe0XPMsBxrJovkeq33'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
## --------------------------


## -- VARAIBLE DECLARATION --
# The list of tweets that we find
tweets = []
# The maximum amount of tweets that we want to use to train the classifier
maximum_tweets = 200
# The amount of user tweets to look through
user_tweet_count = 150
# The words that the user has to tweet about to be a millennial
millennial_words = ['🥑', 'avocado', 'woke', 'bae', 'xennial']
# The minimum proportion of tweets that have to contain milliennial words
minimum_millennial_proportion = 0.01
# A list of emojis that convey positive emotion
positive_emojis = ['😂','❤','😍','😊','💕','😘','☺','👌','😏','😁','😉','👍','🎉','🙌','🙏','love','yummy','delicious']
# A list of emojis that convey negative emotion
negative_emojis = ['😭','😒','😩','😔','☹','💩','😡','😭','😢','😕','😞','🤮','👎','😣','💔','disgusting','gross','awful']
# A list of all the emojis we care about
all_emojis = positive_emojis + negative_emojis
## --------------------------




## ----- TWITTER STREAM -----
class MyStreamListener(tweepy.StreamListener):
    # Calls this everytime a 'status' / tweet is found
    def on_status(self, status):
        try:
	    	# As long as the tweet is longer than 140 chars, get the full text
            text = status.extended_tweet["full_text"]
        except AttributeError:
    		# Otherwise just use the normal text
            text = status.text

    	# Adds the 'status' we are working with to the list of tweets as text minus any unnecessary spaces          
        tweets.append(text.rstrip())
        # When the list of tweets is greater than or equal to 'maximum_tweets'
        if len(tweets) >= maximum_tweets:
        	# Stop listening to the stream
            myStream.disconnect()

    # Catch any errors that may occur
    def on_error(self, status_code):
        if status_code == 420:
            print('Twitter rate limit reached!')
        else:
            print('Error with error code '+str(status_code))
## --------------------------


## --- FETCH SOME TWEETS ----
myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener, tweet_mode='extended')

# Search for tweets with emojis in them
myStream.filter(track=all_emojis, languages=['en'])
## --------------------------


## ---- TWEET FUNCTIONS -----
# Stores the list of all tweets in a file at the specified path
def store_tweets(path, new_tweets):
    # Gets all the old tweets already stored
    with open(path, 'r') as file:
        old_tweets = file.readlines()
    # Combines the list of old tweets and new tweets
    all_tweets = new_tweets + old_tweets
    all_tweets = list(set(all_tweets))
    # Additional clean-up
    all_tweets = [tweet.replace('\n','')+"\n" for tweet in all_tweets]
    # Saves all the tweets to the same file
    with open(path, 'w') as file:
        file.writelines(all_tweets)
    # Return the list of all tweets
    return all_tweets

# Makes the tweets easier to manage and keeps only the necessities
def clean_tweets(tweets):
    # Removes all unnecessay white space, eg. '   Hi    ' -> 'Hi'
    tweets = [tweet.rstrip() for tweet in tweets]
    # Removes all twitter handles, eg. 'Check out @someone' -> 'Check out'
    tweets = [re.sub(r'@\S+', '', tweet) for tweet in tweets]
    # Removes all links, eg. 'Visit https://google.com' -> 'Visit'
    tweets = [re.sub(r'https\S+', '', tweet) for tweet in tweets]
    # Removes punctuation, eg. 'HI!!!!!!!' -> 'HI '
    tweets = [tweet.translate({ord(char): ' ' for char in string.punctuation}) for tweet in tweets]
    # Removes empty tweets (just in case one has crept through)
    tweets = list(filter(None, tweets))
    # Return the list of all clean tweets  
    return tweets

# Splits the list of tweets into positive and negative emotionally charged lists
def sort_tweets(tweets):
    # Get all tweets with positive emojis in it 
    positive_tweets = [tweet for tweet in tweets if set(tweet) & set(positive_emojis)]
    # Do the same for negative tweets
    negative_tweets = [tweet for tweet in tweets if set(tweet) & set(negative_emojis)]
    # Use regex to remove any character that is not an ASCII character
    positive_tweets = [re.sub(r'[^\x00-\x7F]+', '', tweet) for tweet in positive_tweets]
    # Do the same for negative tweets
    negative_tweets = [re.sub(r'[^\x00-\x7F]+', '', tweet) for tweet in negative_tweets]
    # Return both sorted lists
    return positive_tweets, negative_tweets
## --------------------------


## ---- PARSE FUNCTIONS -----
# Removes irrelevant words from a tweet and returns as dictionary
def parse_tweets(words):
    # Makes the whole tweet lowercase
    words = words.lower()
    # Splits the tweet into individual words 
    words = word_tokenize(words)
    # If the word is irrelevant ignore it
    words = [word for word in words if word not in stopwords.words("english")]
    # Creates a dictionary and adds the words as keys and sets each value to TRUE
    word_dictionary = dict([(word, True) for word in words])
    # Returns the dictionary created
    return word_dictionary

# Trains a classifier that will be able to determine if a tweet is positive or negative
def train_classifier(positive_tweets, negative_tweets):
    # Assigns a positive 'tag' to the words in the tweet
    positive_tweets = [(parse_tweets(tweet),'positive') for tweet in positive_tweets]
    # Does the same to negative tweets
    negative_tweets = [(parse_tweets(tweet),'negative') for tweet in negative_tweets]
    # Work out the number of tweets needed for 80% of the positive tweets
    fraction_pos =  round(len(positive_tweets) * 0.8)
    fraction_neg =  round(len(negative_tweets) * 0.8)
        
    train_set = negative_tweets[:fraction_pos] + positive_tweets[:fraction_pos]
    test_set =  negative_tweets[fraction_neg:] + positive_tweets[fraction_neg:]
    classifier = NaiveBayesClassifier.train(train_set)
    accuracy = nltk.classify.util.accuracy(classifier, test_set)
    return classifier, accuracy

def calculate_millennialness(classifier, accuracy, user):
    for name in user:
        try:
            user_tweets = api.user_timeline(screen_name = user, count = user_tweet_count, include_rts = True)
        except tweepy.TweepError as e:
            user = input("the handle you entered was invalid, please try again: ")
        catchcount = 0

    user_tweets = [tweet.text for tweet in user_tweets]
    user_tweets = clean_tweets(user_tweets)

    millennial_tweets = []

    for tweet in user_tweets:
        if any(x in tweet.lower() for x in millennial_words):
            millennial_tweets.append(tweet)

    millennial_tweets_proportion = len(millennial_tweets) / len(user_tweets)

    if len(millennial_tweets) >= 1:
        rating = [classifier.classify(parse_tweets(tweet)) for tweet in millennial_tweets]
        millennial_percent = rating.count ('positive') / len(rating)

        print('\nmillennial-ness: ' + str(round(millennial_percent, 3)) + ' (accuracy: ' + str(round(accuracy * 100, 1))+'%)')
        print('millennial tweets: ' + str(len(millennial_tweets)))
        print('millennial tweet proportion: ' + str(round(millennial_tweets_proportion, 3))+'\n')
    else:
        print('definetly not a millennial.')
## --------------------------

#data = tweets()
#print(data())

## ---- EXECUTE PROGRAM -----
# Gets the path of this .py file
current_path = os.path.abspath(os.path.dirname(__file__))
# Joins paht with file name, 'tweets.txt'
file_path = os.path.join(current_path, "tweets.txt")
# Stores / saves the new tweets we collected to the specified path
tweets = store_tweets(file_path, tweets)
# Cleans the tweets to make the following easier
tweets = clean_tweets(tweets)
# Splits the list of all tweets into two sets, positive and negative 
positive_tweets, negative_tweets = sort_tweets(tweets)
# Using the new tweets, re-train the classifier 
classifier, accuracy = train_classifier(positive_tweets, negative_tweets)
# Get the user's twitter handle
twitter_handle = input("what is your twitter handle?   @")
# Calculate score and determine millennial-ness
calculate_millennialness(classifier, accuracy, twitter_handle)
## --------------------------
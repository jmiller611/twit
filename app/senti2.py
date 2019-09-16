import re
import tweepy
from textblob import TextBlob
import csv
import os
import pandas as pd
import matplotlib
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

api_key = os.environ.get('API_KEY')
api_secret_key = os.environ.get('API_SECRET_KEY')
access_token = os.environ.get('ACCESS_TOKEN')
access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')

#pandas settings
pd.set_option('display.max_colwidth', -1)

def senti(search):
#clean tweet text
    def clean_tweet(tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

#get sentiment from tweet text
    def get_tweet_sentiment(tweet):
        analysis = TextBlob(clean_tweet(tweet))
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0: return 'netural'
        else:
            return 'negative'

#authentication
    auth = tweepy.OAuthHandler(api_key,api_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

#search criteria
    results = api.search(
	q= str(search)+" -filter:retweets", 
	lang='en', 
	result_type='recent', 
	count=100)

    for i in results:
        tweet = clean_tweet(i.text)
        sentiment = get_tweet_sentiment(tweet)

    #test if results.csv exists and remove it if so
    try:
        os.remove('results.csv')
    except OSError:
        pass

    #create the results.csv file to be written
    csvFile = open('results.csv', 'a')

    csvWriter = csv.writer(csvFile)

    for i in results:
        tweet = clean_tweet(i.text)
        sentiment = get_tweet_sentiment(tweet)
        csvWriter.writerow([i.created_at, sentiment, tweet])

    csvFile.close()

    df = pd.read_csv('results.csv', names=['created_at', 'sentiment', 'tweet'])
 
    return df

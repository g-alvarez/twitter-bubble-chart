#!/usr/bin/env python3.6.3

import sys
from tweepy import OAuthHandler
import tweepy
import csv
import twitter_credentials as twitter_cred

NUMBER_OF_ARGUMENTS = 5

def handle_arguments():
    if "-A" not in sys.argv or "-n" not in sys.argv or len(sys.argv) < NUMBER_OF_ARGUMENTS:
        print ("Missing arguments!")
        print ('Hint: "python generate_tweets_csv.py -A <account> -n <number>"')
        sys.exit(0)

    A_arg = ""
    n_arg = 0
    i = 0
    while i < len(sys.argv):
        if sys.argv[i] == "-A":
            A_arg = sys.argv[i+1]
        elif sys.argv[i] == "-n":
            try:
                n_arg = int(sys.argv[i+1])
            except ValueError as e:
                print ("Argument -n must be a number!")
                sys.exit(0)
        i += 1

    return (A_arg, n_arg)

account, total = handle_arguments()

output_csv_file = "tweets.csv"
 
consumer_key = twitter_cred.consumer_key
consumer_secret = twitter_cred.consumer_secret
access_token = twitter_cred.access_token
access_secret = twitter_cred.access_secret
 
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
 
api = tweepy.API(auth)

header = ['Created At', 'Tweet Id', 'Text', 'Source', 'In Reply to', 'Username', 'Screen Name', 'Followers Count', 'Is Retweet']

tweets = [header]

for tweet in tweepy.Cursor(api.user_timeline, id=account).items(total):
    row = []
    row.append(tweet.created_at.strftime('%m/%d/%Y'))
    row.append(tweet.id)
    row.append(tweet.text)
    row.append(tweet.source)
    row.append(tweet.in_reply_to_status_id)
    row.append(tweet.user.name)
    row.append(tweet.user.screen_name)
    row.append(tweet.user.followers_count)
    row.append(True if hasattr(tweet, 'retweeten_status') else False)
    tweets.append(row)

with open(output_csv_file, 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for row in tweets:
    	spamwriter.writerow(row)


# -*- coding: utf-8 -*-
#!/usr/bin/env python3.6.3

import sys
from tweepy import OAuthHandler
import tweepy
import csv
import twitter_credentials as twitter_cred
from tweets_preprocessing import generate_words_count

NUMBER_OF_ARGUMENTS = 5

def handle_arguments():
    """ Handle the arguments from the command line.

    Returns:
        A tuple with the word to be used in the search API and the number of tweets per accounts.

    """
    if "-W" not in sys.argv or "-n" not in sys.argv or len(sys.argv) < NUMBER_OF_ARGUMENTS:
        print ("Missing arguments!")
        print ('Hint: "python generate_tweets_csv.py -W <account> -n <number>"')
        sys.exit(0)

    w_arg = ""
    n_arg = 0
    i = 0
    while i < len(sys.argv):
        if sys.argv[i] == "-W":
            w_arg = sys.argv[i+1]
        elif sys.argv[i] == "-n":
            try:
                n_arg = int(sys.argv[i+1])
            except ValueError as e:
                print ("Argument -n must be a number!")
                sys.exit(0)
        i += 1

    return (w_arg, n_arg)

def get_twitter_api():
    """ Connects to the Twitter API using the credentials in twitter_credentials.py 
        and returns the API object.

    Returns:
        The API object.

    """
    consumer_key = twitter_cred.consumer_key
    consumer_secret = twitter_cred.consumer_secret
    access_token = twitter_cred.access_token
    access_secret = twitter_cred.access_secret

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)

    api = tweepy.API(auth)

    return api

def generate_csv_file(filename, data):
    """ Generate the csv file.

    Args:
        filename: The name of the csv file to be created.
        data: The data to be added. 

    """
    with open(filename, 'w', newline='', encoding="utf-8") as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in data:
            spamwriter.writerow(row)

def generate_tweets_search_csv(api, keyword, output_csv_file):
    """ Generate the csv file with all the tweets found using the search API.

    Args:
        api: The Twitter API.
        keyword: The word used in the search API.
        output_csv_file: The output csv file.

    Returns:
        The list of accounts found in the search API.

    """
    print ("Generating the search api csv...")

    header = ['Created At', 'Tweet Id', 'Text', 'Source', 'In Reply to', 'Username', 
              'Screen Name', 'Followers Count', 'Is Retweet']
    tweets = [header]

    accounts = []

    for tweet in tweepy.Cursor(api.search, q=keyword, count=100, since='2014-01-01').items(100):
        row = []
        row.append(tweet.created_at.strftime('%m/%d/%Y'))
        row.append(tweet.id)
        row.append(tweet.text.replace('\n', ' '))
        row.append(tweet.source)
        row.append(tweet.in_reply_to_status_id)
        row.append(tweet.user.name)
        row.append(tweet.user.screen_name)
        if not tweet.user.screen_name in accounts:
            accounts.append(tweet.user.screen_name)
        row.append(tweet.user.followers_count)
        row.append(True if hasattr(tweet, 'retweeten_status') else False)
        tweets.append(row)

    generate_csv_file(output_csv_file, tweets)

    print ("Done!")
    return accounts

def generate_tweets_per_accounts_csv(api, accounts, total, output_csv_file):
    """ Generate the csv file with n tweets per account.

    Args:
        api: The Twitter API.
        accounts: The accounts to get the tweets from.
        total: The number of tweets per account.
        output_csv_file: The output csv file.

    Returns:
        The list of tweets with the followers_count.

    """
    print ("Generating the tweets per account csv...")

    header = ['Text', 'Followers Count']
    tweets = [header]

    for account in accounts:
        print ("Processing this account: " + account + "...")
        for tweet in tweepy.Cursor(api.user_timeline, id=account).items(total):
            row = []
            row.append(tweet.text.replace('\n', ' '))
            row.append(tweet.user.followers_count)
            tweets.append(row)

    generate_csv_file(output_csv_file, tweets)

    print ("Done!")
    return tweets

def filter_words(words_count):
    """ Filter the words_count list by removing all words that occur less than 10 times.

    Args:
        words_count: The words_count list.

    Returns:
        The filtered list of words_count.

    """
    return [elem for elem in words_count if int(elem[1]) >= 10]

if __name__ == "__main__":

    word, total = handle_arguments()

    api = get_twitter_api()
    accounts = generate_tweets_search_csv(api, word, "tweets_search_result.csv")
    tweets = generate_tweets_per_accounts_csv(api, accounts, total, "tweets.csv")
    words_count = generate_words_count(tweets)

    print ("Generating the words csv...")
    header = ["id", "value"]
    generate_csv_file("../words.csv", [header] + filter_words(words_count))
    print ("Done!")
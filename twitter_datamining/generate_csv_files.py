# -*- coding: utf-8 -*-
#!/usr/bin/env python3.6.3

import sys
from tweepy import OAuthHandler
import tweepy
import csv
import twitter_credentials as twitter_cred
from tweets_preprocessing import get_words_count, get_ngrams_count
import statistics
import timeit

NUMBER_OF_ARGUMENTS = 5
TWEETS_PER_QUERY = 100

def handle_arguments():
    """ Handle the arguments from the command line.

    Returns:
        A tuple with the word to be used in the search API and the number of tweets per accounts.

    """
    if "-W" not in sys.argv or "-n" not in sys.argv or len(sys.argv) < NUMBER_OF_ARGUMENTS:
        print ("Missing arguments!")
        print ('Hint: "python generate_csv_files.py -W <account> -n <number>"')
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

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

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

def get_tweets(api_result, accounts):
    """ Generates the list of tweets from the result of the search API.

    Args:
        api_result: The result of the search API.

    Returns:
        The list of tweets found in the search API.

    """
    tweets = []
    for tweet in api_result:
        row = []
        row.append(tweet.created_at.strftime('%m/%d/%Y'))
        row.append(tweet.id)
        row.append(tweet.text)
        row.append(tweet.source)
        row.append(tweet.in_reply_to_status_id)
        row.append(tweet.user.name)
        row.append(tweet.user.screen_name)
        if not tweet.user.screen_name in accounts:
            accounts.append(tweet.user.screen_name)
        row.append(tweet.user.followers_count)
        row.append(True if hasattr(tweet, 'retweeted_status') else False)
        tweets.append(row)
    return tweets

def generate_tweets_search_api_csv(api, keyword, output_csv_file):
    """ Generate the csv file with all the tweets found using the search API.

    Args:
        api: The Twitter API.
        keyword: The word used in the search API.
        output_csv_file: The output csv file.

    Returns:
        The list of accounts found in the search API.

    """
    print ("Generating the tweets found in the search api csv...")

    header = ['Created At', 'Tweet Id', 'Text', 'Source', 'In Reply to', 'Username', 
              'Screen Name', 'Followers Count', 'Is Retweet']
    tweets = [header]

    accounts = []

    since_id = None
    max_id = -1
    while True:
        print ("Processing 100 tweets...")
        if max_id <= 0:
            if not since_id:
                api_result = api.search(q=keyword, count=TWEETS_PER_QUERY, since='2014-01-01')
                tweets += get_tweets(api_result, accounts)
            else:
                api_result = api.search(q=keyword, count=TWEETS_PER_QUERY, since='2014-01-01', 
                             since_id=since_id)
                tweets += get_tweets(api_result, accounts)
        else:
            if not since_id:
                api_result = api.search(q=keyword, count=TWEETS_PER_QUERY, since='2014-01-01', 
                             max_id=str(max_id - 1))
                tweets += get_tweets(api_result, accounts)
            else:
                api_result = api.search(q=keyword, count=TWEETS_PER_QUERY, since='2014-01-01', 
                             max_id=str(max_id - 1), since_id=since_id)
                tweets += get_tweets(api_result, accounts)
        if not api_result:
            print("No more tweets found...")
            break
        max_id = api_result[-1].id

    generate_csv_file(output_csv_file, tweets)

    generate_csv_file("../csv/accounts_found.csv", ["account"] + [[account] for account in accounts])

    print ("Done!")
    return (accounts, tweets)

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
    print ("Total accounts to be processed: ", len(accounts))

    header = ['Created At', 'Tweet Id', 'Text', 'Source', 'In Reply to', 'Username', 
              'Screen Name', 'Followers Count', 'Is Retweet']
    tweets = [header]

    for account in accounts:
        print ("Processing this account: " + account + "...")
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
            row.append(True if hasattr(tweet, 'retweeted_status') else False)
            tweets.append(row)

    generate_csv_file(output_csv_file, tweets)

    print ("Done!")
    return tweets

def filter_words(words_count, ngrams=False, keyword=""):
    """ Filter the words_count list by getting taking only the elements that are higher than the mean + sd.

    Args:
        words_count: The words_count list.
        ngrams: Indicates if the list is a ngram list or not.
        keyword: The word to be removed from the list.

    Returns:
        The filtered list of words_count.

    """
    if ngrams:
        if len(words_count) >= 20:
            filtered_words_count = [word for word in words_count if not keyword in word[0].lower() and word[1] > 1]
        else:
            filtered_words_count = [word for word in words_count if not keyword in word[0].lower()]
    else:
        if len(words_count) >= 20:
            filtered_words_count = [word for word in words_count if word[0].lower() != keyword and word[1] > 1]
        else:
            filtered_words_count = [word for word in words_count if word[0].lower() != keyword]
    mean = statistics.mean([word[1] for word in filtered_words_count])
    try:
        std = statistics.stdev([word[1] for word in filtered_words_count])
    except:
        std = 0
    return [word for word in filtered_words_count if word[1] >= mean + std]

def filter_hashtags(words_count):
    """ Filter the words_count list by getting only the hashtags.

    Args:
        words_count: The words_count list.

    Returns:
        The filtered list of words_count.

    """
    if len(words_count) >= 20:
        filtered_hashtags = [word for word in words_count if word[0][0] == "#" and word[1] > 1]
    else:
        filtered_hashtags = [word for word in words_count if word[0][0] == "#"]
    mean = statistics.mean([word[1] for word in filtered_hashtags])
    try:
        std = statistics.stdev([word[1] for word in filtered_hashtags])
    except:
        std = 0
    return  [word for word in filtered_hashtags if word[1] >= mean + std]

if __name__ == "__main__":

    start_time = timeit.default_timer()

    word, total = handle_arguments()

    print ("")
    print ("Word:", word, "-- Tweets per account:", total)
    print ("")

    api = get_twitter_api()
    accounts, tweets_search_api = generate_tweets_search_api_csv(api, word, "../csv/tweets_search_api.csv")
    tweets_per_accounts = generate_tweets_per_accounts_csv(api, accounts, total, "../csv/tweets_per_accounts.csv")
    words_count_search_api = get_words_count(tweets_search_api, text_column=2)
    words_count_per_accounts = get_words_count(tweets_per_accounts, text_column=2)
    ngrams_count_per_accounts = get_ngrams_count(tweets_per_accounts, text_column=2)

    print ("Generating the words csv from the tweets per accounts...")
    header = ["word", "value"]
    generate_csv_file("../csv/1_words_per_accounts.csv", [header] + words_count_per_accounts)
    print ("Done!")

    print ("Generating the words csv from the tweets found in the search api...")
    header = ["word", "value"]
    generate_csv_file("../csv/1_words_search_api.csv", [header] + words_count_search_api)
    print ("Done!")

    print ("Generating the words csv from hashtags found in tweets per accounts...")
    header = ["word", "value"]
    generate_csv_file("../csv/1_words_hashtags_search_api.csv", [header] + [word for word in words_count_per_accounts if word[0][0] == "#"])
    print ("Done!")

    print ("Generating the ngrams csv from tweets per accounts...")
    header = ["word", "value"]
    generate_csv_file("../csv/1_ngrams_search_api.csv", [header] + ngrams_count_per_accounts)
    print ("Done!")

    print ("Generating the filtered words csv from the tweets per accounts...")
    header = ["word", "value"]
    generate_csv_file("../csv/1_filtered_words_per_accounts.csv", [header] + filter_words(words_count_per_accounts, keyword=word.lower()))
    print ("Done!")

    print ("Generating the filtered words csv from the tweets found in the search api...")
    header = ["word", "value"]
    generate_csv_file("../csv/1_filtered_words_search_api.csv", [header] + filter_words(words_count_search_api, keyword=word.lower()))
    print ("Done!")

    print ("Generating the filtered words csv from hashtags found in tweets per accounts...")
    header = ["word", "value"]
    generate_csv_file("../csv/1_filtered_words_hashtags_search_api.csv", [header] + filter_hashtags(words_count_per_accounts))
    print ("Done!")

    print ("Generating the filtered ngrams csv from tweets per accounts...")
    header = ["word", "value"]
    generate_csv_file("../csv/1_filtered_ngrams_search_api.csv", [header] + filter_words(ngrams_count_per_accounts, ngrams=True, keyword=word.lower()))
    print ("Done!")

    print("Program Executed in ", timeit.default_timer() - start_time, "seconds")
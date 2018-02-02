#!/usr/bin/env python3

import os.path
import re
import requests
import sys
import time
from configparser import ConfigParser
from datetime import datetime

from praw import Reddit

CONFIG_FILE = 'config.ini'
LOG_FILE    = 'completed.log'

GFYCAT_API_TOKEN = 'https://api.gfycat.com/v1/oauth/token'
GFYCAT_API_SEND = 'https://api.gfycat.com/v1/gfycats'

def read_config():
    config = ConfigParser()
    config.read(CONFIG_FILE)

    return config

# Requests gfycat to create a gif from a given URL
def send_url_to_gfycat(url, token):
    r = requests.post(GFYCAT_API_SEND,
        json={'fetchUrl': url},
        headers={'Authorization': 'Bearer ' + token})
    print('Send:', r.status_code, r.json())

# Mark a submission as already processed, so that it is skipped the next time it's encountered
def log_processed(submission, gfycat_id):
    with open(LOG_FILE, 'a') as f:
        f.write(','.join([str(datetime.now()), submission.id, 'https://reddit.com/r' + submission.permalink, 'https://gfycat.com/' + gfycat_id]) + '\n')

# Get a list of ids of already processed submissions
def read_processed_submissions():
    if not os.path.isfile(LOG_FILE):
        return []

    completed = []
    with open(LOG_FILE, 'r') as f:
        for line in f:
            completed.append(line.split(',')[1])

    return completed

def main():
    config  = read_config()

    # Log in to Reddit
    reddit_config = config['reddit']
    reddit        = Reddit(client_id=reddit_config['client_id'],
        client_secret=reddit_config['client_secret'],
        username=reddit_config['username'],
        password=reddit_config['password'],
        user_agent=reddit_config['user_agent'])
    print("Logged in to Reddit as:", reddit.user.me())

    # Get a gfycat token
    gfycat_config = config['gfycat']
    r = requests.post(GFYCAT_API_TOKEN, json={
        'grant_type': 'password',
        'client_id': gfycat_config['client_id'],
        'client_secret': gfycat_config['client_secret'],
        'username': gfycat_config['username'],
        'password': gfycat_config['password']})
    print('Get gfycat token:', r.status_code)
    try:
        gfycat_token = r.json()['access_token']
    except(KeyError):
        print(r.json())
        sys.exit(1)

    if (len(sys.argv) > 1):
        send_url_to_gfycat(sys.argv[1], gfycat_token)

    # Read the list of watched subreddits
    watched_subreddits = re.split('\s+', config['preferences']['subreddits'].strip())
    print('Watching:', watched_subreddits)
    watchlist = '+'.join(watched_subreddits)

    # Read the polling interval
    try:
        interval = int(config['preferences']['interval'])
    except(ValueError):
        print('Invalid interval:', config['preferences']['interval'] + '.', 'Using default: 300.', file=sys.stderr)
        interval = 300

    # Main loop: get new submissions, find the ones we're interested in, create gfycat mirrors, save them to a file so we don't process them twice, sleep for the specified interval, then repeat
    while True:
        already_processed = read_processed_submissions()

        for submission in reddit.subreddit(watchlist).new(limit=10):
            if(submission.id in already_processed):
                continue

            # TODO: convert if required
            print(submission.permalink)
            log_processed(submission, '???')

        time.sleep(interval)
        # TODO: we may need to refresh API tokens from time to time

if __name__ == '__main__':
    main()


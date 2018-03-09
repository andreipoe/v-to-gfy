#!/usr/bin/env python3

import os.path
import re
import requests
import signal
import sys
import time
import traceback
from configparser import ConfigParser
from datetime import datetime
from pprint import pprint

import praw.models
from praw import Reddit

CONFIG_FILE = 'config.ini'
LOG_FILE    = 'completed.log'
ERROR_FILE  = 'failed.log'

GFYCAT_BASE_URL = 'https://gfycat.com/'

GFYCAT_API_TOKEN  = 'https://api.gfycat.com/v1/oauth/token'
GFYCAT_API_SEND   = 'https://api.gfycat.com/v1/gfycats'
GFYCAT_API_STATUS = 'https://api.gfycat.com/v1/gfycats/fetch/status/'

GFYCAT_STATUS_INTERVAL = 5

COMMENT_MSG = """Here is a [Gfycat mirror of this submission's video](https://gfycat.com/{}).

Because v.redd.it does not expose direct media links, sharing the video without the comments page is cumbersome. The Gfycat is a direct media link that can be viewed on virtually all platforms. [About this bot](https://github.com/andreipoe/v-to-gfy)."""
PM_MSG      = """Hi /u/{},

I've mirrored all the submissions to v.redd.it that I could find in your PM. Here are the links:

{}

Thanks for using your local friendly Reddit bot!

&nbsp;

***

^(You can also mention me in a comment to generate a mirror for the parent submission. More) [^(about this bot)](https://github.com/andreipoe/v-to-gfy)^.

^(Something wrong or missing?) [^(Open an issue)](https://github.com/andreipoe/v-to-gfy/issues)^(. Please make sure to include the submission URL and the bot's reply (if any)^) ^(in your bug report.)"""
MENTION_MSG = """Here is a [Gfycat mirror of this submission's video]({}). This makes it easier to share the content without the Reddit comments section.

Thanks for using your local friendly Reddit bot!

***

^(You can also) [^(send me a PM)](https://www.reddit.com/message/compose/?to=v-to-gfy_bot&subject=Mirror&message=Paste%20links%20to%20v.redd.it%20submission%20below%2C%20one%20per%20line.%20You%20will%20receive%20a%20single%20reply%20with%20a%20mirror%20for%20each%20valid%20v.redd.it%20link.%20Other%20links%20and%20text%20will%20be%20ignored.%0D%0A%0D%0A%3CYOUR%20LINKS%20HERE%3E) ^(with one or more v.redd.it links and I'll respond with Gfycat mirror links. More) [^(about this bot)](https://github.com/andreipoe/v-to-gfy)^.

^(Something wrong or missing?) [^(Open an issue)](https://github.com/andreipoe/v-to-gfy/issues)^(. Please make sure to include the submission URL and the bot's reply (if any)^) ^(in your bug report.)"""

def read_config():
    config = ConfigParser()
    config.read(CONFIG_FILE)

    return config

# Request gfycat to create a gif from a given URL and wait until the job completes (or fails)
def send_url_to_gfycat(url, duration, token):
    r = requests.post(GFYCAT_API_SEND,
        json={'fetchUrl': url, 'cut': {'start': 0, 'duration': duration}},
        headers={'Authorization': 'Bearer ' + token})
    print('Send:', r.status_code, r.json())

    if r.status_code != 200:
        return None
    else:
        gfyname  = r.json()['gfyname']
        status = requests.get(GFYCAT_API_STATUS + gfyname).json()
        print(status)
        while status['task'] == 'encoding':
            time.sleep(GFYCAT_STATUS_INTERVAL)
            status = requests.get(GFYCAT_API_STATUS + gfyname).json()
            print(status)

        if status['task'] == 'complete':
            return status['gfyname']

        if status['task'] == 'error':
            print('Gfycat task error:', status, file=sys.stderr)
        else:
            print('Unknown gfycat status:', status, file=sys.stderr)
        return None

# Mark a submission as already processed, so that it is skipped the next time it's encountered
def log_processed(submission, gfyname):
    if gfyname is not None:
        fname = LOG_FILE
    else:
        fname   = ERROR_FILE
        gfyname = 'error'

    with open(fname, 'a') as f:
        f.write(','.join([str(datetime.now()), submission.id, 'https://reddit.com/r' + submission.permalink, GFYCAT_BASE_URL + gfyname]) + '\n')

# Get a list of ids of already processed submissions
def read_processed_submissions():
    if not os.path.isfile(LOG_FILE):
        return []

    completed = []
    with open(LOG_FILE, 'r') as f:
        for line in f:
            completed.append(line.split(',')[1])

    return completed

# Create a gfycat mirror of a submission's video
def mirror_to_gfy(submission, reddit, gfycat_token):
    try:
        video    = submission.media['reddit_video']['fallback_url']
        duration = submission.media['reddit_video']['duration']
    except TypeError:
        # If the submission is a x-post, the video url isn't available directly, so we need to get it from the original submission
        xpost_url = requests.get(submission.url).url
        xpost     = reddit.submission(url=xpost_url)
        video     = xpost.media['reddit_video']['fallback_url']
        duration  = xpost.media['reddit_video']['duration']

    # gfycay supports a maximum length of 60 seconds, so reject videos that exceed this duration
    if duration > 60:
        return None

    return send_url_to_gfycat(video, duration, gfycat_token)

# Parse a string and extract all URLs to reddit.com or v.redd.it
def detect_urls_in_text(text):
    words  = text.strip().split()
    re_url = re.compile(r'(?:(?:https?):\/\/)?(?:(?:www\.|)reddit\.com|v\.redd\.it)\/\S+')

    return [w for w in words if re_url.match(w)]

# Main loop to monitor new submissions with v.redd.it content
def submissions_loop(reddit, gfycat_token):
    already_processed = read_processed_submissions()

    for submission in reddit.subreddit(watchlist).new(limit=10):
        if submission.id in already_processed or 'v.redd.it' not in submission.url:
            continue

        print(submission.permalink + ',', submission.url)

        gfyname = mirror_to_gfy(submission, reddit, gfycat_token)
        # TODO: Post a reddit message when creating mirror succeeds
        if gfyname is not None:
            print(COMMENT_MSG.format(gfyname))
        log_processed(submission, gfyname)

# Main loop to check and respond to private messages
def pm_loop(reddit, gfycat_token):
    for m in reddit.inbox.unread():
        if not isinstance(m, praw.models.Message):
            continue

        # Extract the URLs in the body of the received message
        urls = detect_urls_in_text(m.body)
        print('Received PM from', m.author, 'containing v.redd.it links:', urls)

        # Create mirrors for each extracted URL
        mirrors = {}
        for u in urls:
            try:
                mirror = GFYCAT_BASE_URL + mirror_to_gfy(reddit.submission(url=u), reddit, gfycat_token)
            except:
                mirror = 'FAILED'
            mirrors[u] = mirror

        print('Responding to PM from', m.author, 'with mirrors:')
        pprint(mirrors)

        # Craft a PM reply
        mirrors_text = '\n'.join('* {} -- {}'.format(v, mirror) for v,mirror in mirrors.items())
        reply = PM_MSG.format(m.author, mirrors_text)

        # Send the reply and mark the message as read so that we don't process it again
        replied = False
        while not replied:
            try:
                m.reply(reply)
                replied = True
            except praw.exceptions.APIException as err:
                if err.error_type == 'RATELIMIT':
                    print('Reddit ratelimit hit. Waiting 10 minutes, then retrying...', file=sys.stderr)
                    time.sleep(600)
                else:
                    raise

        m.mark_read()

# Main loop to check and respond to mentions
def mention_loop(reddit, gfycat_token):
    for m in reddit.inbox.unread():
        if not isinstance(m, praw.models.Comment):
            continue

        print('Received mention from', m.author, 'with URL:', 'https://reddit.com/r' + m.submission.permalink)
        if 'v.redd.it' not in m.submission.url:
            print('Not a v.redd.it submission')

        try:
            mirror = GFYCAT_BASE_URL + mirror_to_gfy(m.submission, reddit, gfycat_token)
        except:
            continue

        print('Responding to mention from', m.author, 'with mirror:', mirror)
        reply = MENTION_MSG.format(mirror)

        # Send the reply and mark the message as read so that we don't process it again
        replied = False
        while not replied:
            try:
                m.reply(reply)
                replied = True
            except praw.exceptions.APIException as err:
                if err.error_type == 'RATELIMIT':
                    print('Reddit ratelimit hit. Waiting 10 minutes, then retrying...', file=sys.stderr)
                    time.sleep(600)
                else:
                    raise

        m.mark_read()

# Print a friendly message when receiving Ctrl-C
def sigint_handler(signal, frame):
    print("Received SIGINT, shutting down...", file=sys.stderr)
    sys.exit(0)

def main():
    config = read_config()

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

    # TODO: debugging
    if (len(sys.argv) > 1):
        gfyname = mirror_to_gfy(reddit.submission(url=sys.argv[1]), reddit, gfycat_token)
        print(GFYCAT_BASE_URL + gfyname)
        sys.exit(0)

    # Read enabled components
    prefs_config = config['preferences']
    enabled = {c:prefs_config.getboolean('enable_'+c+'_monitoring') for c in ['subreddit', 'pm', 'mention']}
    print("Components enabled:", [c for c in enabled.keys() if enabled[c] == True])

    # Read the list of watched subreddits if monitoring subreddits is enabled
    if enabled['subreddit']:
        watched_subreddits = re.split('\s+', prefs_config['subreddits'].strip())
        print('Watching:', watched_subreddits)
        watchlist = '+'.join(watched_subreddits)

    # Read the polling interval
    try:
        interval = int(prefs_config['interval'])
    except(ValueError):
        print('Invalid interval:', prefs_config['interval'] + '.', 'Using default: 300.', file=sys.stderr)
        interval = 300
    print('Interval between checks:', interval, 'seconds')

    signal.signal(signal.SIGINT, sigint_handler)

    # Main loop: get new submissions, find the ones we're interested in, create gfycat mirrors, save them to a file so we don't process them twice, sleep for the specified interval, then repeat
    while True:
        try:
            # Mirror recent submissions
            if enabled['subreddit']:
                submissions_loop(reddit, gfycat_token)

            # Create mirrors on-demand for submissions sent by PM
            if enabled['pm']:
                pm_loop(reddit, gfycat_token)

            if enabled['mention']:
                mention_loop(reddit, gfycat_token)

        except Exception as err:
            print('Error:', err, file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            print('Waiting', 2*interval, 'seconds, then restarting...', file=sys.stderr)
            time.sleep(interval)

        time.sleep(interval)

        # TODO: we may need to refresh API tokens from time to time

if __name__ == '__main__':
    main()


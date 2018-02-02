#!/usr/bin/env python3

import requests
from configparser import ConfigParser

from praw import Reddit

def read_config():
    config = ConfigParser()
    config.read('config.ini')

    return config

def main():
    config  = read_config()

    # Log in to Reddit
    reddit_config = config['reddit']
    reddit        = Reddit(client_id=reddit_config['client_id'],
        client_secret=reddit_config['client_secret'],
        password=reddit_config['password'],
        user_agent=reddit_config['user_agent'],
        username=reddit_config['username'])
    print("Logged in to Reddit as:", reddit.user.me())

    # Get a gfycat token
    gfycat_config = config['gfycat']
    r = requests.post('https://api.gfycat.com/v1/oauth/token', json={
        'grant_type': 'client_credentials',
        'client_id': gfycat_config['client_id'],
        'client_secret': gfycat_config['client_secret']})
    print('Get gfycat token:', r.status_code)

if __name__ == '__main__':
    main()


#!/usr/bin/env python3

import sys
import requests
from configparser import ConfigParser

from praw import Reddit

def read_config():
    config = ConfigParser()
    config.read('config.ini')

    return config

# Requests gfycat to create a gif from a given URL
def send_url_to_gfycat(url, token):
    r = requests.post('https://api.gfycat.com/v1/gfycats',
        json={'fetchUrl': url},
        headers={'Authorization': 'Bearer ' + token})
    print('Send:', r.status_code, r.json())

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
    r = requests.post('https://api.gfycat.com/v1/oauth/token', json={
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

if __name__ == '__main__':
    main()


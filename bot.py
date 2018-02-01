#!/usr/bin/env python3

from praw import Reddit
from configparser import ConfigParser

def read_config():
    config = ConfigParser()
    config.read('config.ini')

    return config

def main():
    config = read_config()
    account = config['account']

    reddit = Reddit(client_id=account['client_id'],
        client_secret=account['client_secret'],
        password=account['password'],
        user_agent=account['user_agent'],
        username=account['username'])

    print("Logged in as:", reddit.user.me())

if __name__ == '__main__':
    main()


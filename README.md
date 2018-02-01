# v-to-gfy

This is a [Reddit](https://reddit.com) bot creates [gfycat](https://gfycat.com/) mirrors for popular video submissions using Reddit's own v.redd.it service.

## Motivation 

v.redd.it links are different from most other content posted on Reddit, since there no direct video URL is exposed. Instead, clicking such a post opens the Reddit comments page. This makes sharing the content (and the content) alone clumsy. 

## Principle of operation

This bot regularly scrapes a number of subreddits and automatically creates gfycat mirros of popular video sumissions that use v.redd.it. Gfycat content can be viewed on all platforms, and the content is served alone, without any discussion threads.

The bot also accepts private messages to create mirrors on demand. On receiving a message, the bot will take all direct v.redd.it links and links to Reddit threads that contain v.redd.it media and will upload the content to gfycat. When done, it will reply with the new links. All other message content is discared.

## Running your own bot

You can easily run your own copy of the v-to-gfy bot.

### Requirements 

* A server connected to the Internet and capable of running Python 3.
* [PRAW](http://praw.readthedocs.io/en/latest/getting_started/installation.html).
* A Reddit account for the bot. **WARNING**: Do **not** use your main Reddit accout for the bot -- you **will** get banned from subreddits that don't allow bots or don't want this bot in particular.
* A gfycat account to upload to.

### Set up

1. Obtain the code, e.g. by cloning this repository:

    ```
    git clone https://github.com/andreipoe/v-to-gfy.git
    ```

2. Set up your access credentials: 
   1. Copy `config.ini.template` to `config.ini`.
   2. Open `config.ini` and set your credentials under the `account` section according to the [PRAW script application authentication docs](http://praw.readthedocs.io/en/latest/getting_started/authentication.html).
3. Set up your bot preferences. **TODO**.


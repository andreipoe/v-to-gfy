# v-to-gfy

This is a [Reddit](https://reddit.com) bot creates [gfycat](https://gfycat.com/) mirrors for popular video submissions using Reddit's own v.redd.it service.

## Motivation

v.redd.it links are different from most other content posted on Reddit, since there no direct video URL is exposed. Instead, clicking such a post opens the Reddit comments page. This makes sharing the content (and the content) alone clumsy.

## Usage

The bot obtains content to mirror from 3 sources:

1. Automatiically scraping subreddits and checking for v.redd.it content links.
2. PMs from users containing links to v.redd.it posts.
3. Mentions in the comments of a v.reddd.it post.

In all cases, it automatically creates gfycat mirros of the v.redd.it content. Gfycat content can be viewed on all platforms, and the content is served on a dedicated page, without any discussion threads.

### Invoking the bot on demand

PMs to the bot will be scanned for reddit post links. A mirror will be created for each valid link detected, and a single reply will be sent to the author of the PM containing all the mirror. All other body text, as well as the PM's subject, is ignored.

When mentioned in the comments of a post, the bot will use the post's content to create a mirror, and then it will reply to the comment's author. It will disregard all message text, so you cannot use this way to ask for additinal mirrors. This is done to avoid derailing discussions.

## Upcoming features and improvements

Soon<sup>TM</sup>, the bot will support:

* Mirroring submissions containing audio to Streamable instead of Gfycat.

---------------------------------------

## Running your own bot

You can easily run your own copy of the v-to-gfy bot. **This section is under development**.

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
   2. Open `config.ini` and set your Reddit credentials under the `reddit` section according to the [PRAW script application authentication docs](http://praw.readthedocs.io/en/latest/getting_started/authentication.html).
   3. Open `config.ini` and set your gfycat credentials under the `gfycat` section using the details received by email after following the [access token procedure](https://developers.gfycat.com/api/#quick-start). Note that you also need your account's username and password, as per the [Password Grant docs](https://developers.gfycat.com/api/#password-grant).
3. Set up your bot preferences. **TODO**.

---------------------------------------

## Acknowledgements

This bot would not be possible without [the wonderful PRAW](https://github.com/praw-dev/praw), [the Reddit API](https://www.reddit.com/dev/api), and [the Gfycat API](https://developers.gfycat.com/). A big "thank you" to everyone who has contributed to developing these projects an making them freely available.


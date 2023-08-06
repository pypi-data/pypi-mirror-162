# Text to tweets

This small package simply splits a large block of text into 280 character chunks.

The code is lifted wholesale from https://github.com/NaruBeast/tweet-splitter.

## Install

``` bash
pip3 install text-to-tweets
```

## Usage

``` python3
from text_to_tweets import tweet_splitter

tweets = tweet_splitter(
    article_text,
    counter=True  # Add counters to tweets - e.g. "(3/10)"
)
```

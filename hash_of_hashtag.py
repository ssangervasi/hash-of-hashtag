import argparse
from datetime import datetime, timedelta
from hashlib import sha256
from collections import namedtuple
import time

import twitter


def main():
    parser = create_argument_parser()
    args = parser.parse_args()
    if args.command == 'run':
        run_forever(args)


def create_argument_parser():
    parser = argparse.ArgumentParser()
    command_group = parser.add_argument_group('Commands')
    command_group.add_argument(
        'command',
        choices=['run'],
        help=(
            'Run until interrupted.'
            ' While running, a post is made every 5 minutes'
            ' using the top hashtag from twitter\'s "trending" API.'
            ' The same hashtag will not be used more than once'
            ' during a session, but this history is not saved'
            ' between executions of the "run" command.'
        ),
    )
    command_group.add_argument(
        '--ignore',
        nargs='*',
        help=(
            'A list of any number of hashtags to ignore completely.'
            ' Tags can be of the form "DaftPunk" or "#DaftPunk"'
            ' -- these are considered equal.'
        ),
    )
    auth_group = parser.add_argument_group(
        'Auth Credentials',
        description='These arguments are required for all API access.'
    )
    auth_group.add_argument(
        '--consumer-key',
        required=True,
    )
    auth_group.add_argument(
        '--consumer-secret',
        required=True,
    )
    auth_group.add_argument(
        '--access-token-key',
        required=True,
    )
    auth_group.add_argument(
        '--access-token-secret',
        required=True,
    )
    return parser


def run_forever(args):
    api = twitter.Api(
        consumer_key=args.consumer_key,
        consumer_secret=args.consumer_secret,
        access_token_key=args.access_token_key,
        access_token_secret=args.access_token_secret,
    )
    print(f'Will ignore tags: {args.ignore}')
    hash_poster = HashPoster(api, ignored_tags=args.ignore)
    delay_delta = timedelta(minutes=5)
    while True:
        if delay_delta > hash_poster.get_time_since_last_post():
            sleep_delta(delay_delta)
            continue
        print(f'Getting top hashtag...')
        top_hashtag = hash_poster.get_top_hashtag()
        if top_hashtag is None:
            print('No fresh hashtags.')
            sleep_delta(delay_delta)
            continue
        print(f'Posting hashtag "{top_hashtag}"...')
        hash_poster.post_hashtag_hash(top_hashtag)
        print(f'Done.')


def sleep_delta(delay_delta):
    sleep_seconds = delay_delta.total_seconds()
    print(f'Going to sleep for {sleep_seconds} seconds.')
    time.sleep(sleep_seconds)


class Hashtag:

    def __init__(self, tag):
        (_, self.tag) = self.split_tag(tag)

    def __repr__(self):
        return f'Hashtag({self})'

    def __str__(self):
        return f'#{self.tag}'

    @classmethod
    def is_hashtag(cls, possible_tag):
        return (
            possible_tag is not None
            and len(possible_tag) > 1
            and cls.has_hash(possible_tag)
        )

    @classmethod
    def has_hash(cls, tag):
        return tag[0] == '#'

    @classmethod
    def split_tag(cls, tag):
        real_tag = tag
        if cls.has_hash(tag):
            real_tag = tag[1:]
        return ('#', real_tag)


class HashPoster:
    PostHistoryEntry = namedtuple(
        'PostHistoryEntry',
        ('hashtag', 'hashtag_hash', 'post_time')
    )

    def __init__(self, api, ignored_tags=None):
        self.api = api
        self.last_post = None
        self.post_history = {}
        self.ignored_tags = set()
        if ignored_tags is not None:
            self.ignored_tags.update(Hashtag(tag).tag for tag in ignored_tags)

    def get_trending_hashtags(self):
        trends = self.api.GetTrendsCurrent()
        hashtags = [
            hashtag
            for hashtag in map(self.get_hashtag_from_trend, trends)
            if hashtag is not None
            and hashtag.tag not in self.post_history
            and hashtag.tag not in self.ignored_tags
        ]
        return hashtags

    def get_top_hashtag(self):
        trending_hashtags = self.get_trending_hashtags()
        if len(trending_hashtags) == 0:
            return None
        return trending_hashtags[0]

    def post_hashtag_hash(self, hashtag):
        hashtag_hash = self.hash_hashtag(hashtag)
        self.api.PostUpdate(self.format_post(hashtag, hashtag_hash))
        self.last_post = self.PostHistoryEntry(
            hashtag,
            hashtag_hash,
            datetime.now(),
        )
        self.post_history[hashtag.tag] = self.last_post
        return self.last_post

    def format_post(self, original, hashed):
        return f'{hashed} {original} #HashOfHashtag'

    def get_time_since_last_post(self):
        if self.last_post is None:
            return timedelta.max
        return datetime.now() - self.last_post.post_time

    @classmethod
    def get_hashtag_from_trend(cls, trend):
        name = trend.name
        if Hashtag.is_hashtag(name):
            return Hashtag(name)
        return None

    @classmethod
    def hash_hashtag(cls, hashtag, algorithm=sha256):
        tag_hash = algorithm(hashtag.tag.encode('utf-8'))
        return Hashtag(tag_hash.hexdigest())


if __name__ == '__main__':
    main()

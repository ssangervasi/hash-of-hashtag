# hash-of-hashtag
A little twitter bot for posting the cryptographic hash of trending hashtags.

## Requirements
* python ~= 3.6
* python-twitter ~= 3.3

## Usage
There is currently only one command supported: `run`.

In this mode, a Twitter API client connection is created using the arguments
from the "Auth Credentials" group. Then the program runs continuously,
querying Twitter every 5 minutes to check the top trending hashtags.

If there is a newly-trending hashtag that has not been hashed already,
then the program calculates the SHA256 hash of that string (omitting the
leading "#" symbol). It then posts a new tweet on the user's behalf,
using the hash's hexidecimal representation as a hashtag, the original
hashtag, and "#HashOfHashtag" in the body of the tweet.

For example:
```
#6fcb8d8690bb1ccdd9d7eed9e606ba52d788ad75c6bd037f87fc62bdf5d1cf3f #pechinoexpress #HashOfHashtag
```

Once this is posted, or there if there were no newly-trending hashtags,
the program goes to sleep for another 5 minutes.

In this mode, the same hashtag will not be used multiple times.
This history, however, is not saved between executions. You can add
any number of hashtags to ignore during execution with the `--ignore`
argument.

For example, the following command will never make a post that uses
"#IgnoreMe" or "#AndAlsoMe":

`python hash_of_hashtag.py run --ignore IgnoreMe AndAlsoMe <auth credentials>`

## Command-Line Help
```
usage: hash_of_hashtag.py [-h] [--ignore [IGNORE [IGNORE ...]]] --consumer-key
                          CONSUMER_KEY --consumer-secret CONSUMER_SECRET
                          --access-token-key ACCESS_TOKEN_KEY
                          --access-token-secret ACCESS_TOKEN_SECRET
                          {run}

optional arguments:
  -h, --help            show this help message and exit

Commands:
  {run}                 Run until interrupted. While running, a post is made
                        every 5 minutes using the top hashtag from twitter's
                        "trending" API. The same hashtag will not be used more
                        than once during a session, but this history is not
                        saved between executions of the "run" command.
  --ignore [IGNORE [IGNORE ...]]
                        A list of any number of hashtags to ignore completely.
                        Tags can be of the form "DaftPunk" or "#DaftPunk" --
                        these are considered equal.

Auth Credentials:
  These arguments are required for all API access.

  --consumer-key CONSUMER_KEY
  --consumer-secret CONSUMER_SECRET
  --access-token-key ACCESS_TOKEN_KEY
  --access-token-secret ACCESS_TOKEN_SECRET
```

## To-Do
* Create `setup.py` to install module with command-line hooks.
* A command for posting a single hash-of-hashtag instead of querying the trending list.
* Add more options to the `run` command, such as:
  * The amount of time to sleep between posts.
  * A file path to read as the ignore/history list.
  * A file path to which to write the history.
* Better error handling for the `run` command when, for example, the formatted post is longer than 140 chars.

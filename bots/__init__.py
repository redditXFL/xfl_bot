import praw

SUBREDDIT = "XFLDev"

# Reddit settings
reddit = praw.Reddit('xfl_bot')
subreddit = reddit.subreddit(SUBREDDIT)
redditor = reddit.redditor('XFL_Bot')

# Post Flairs
_POST_FLAIR_GAME_THREAD_XFLDEV = "68b36adc-4ed0-11ea-a022-0e2cad60f66f"
_POST_FLAIR_GAME_THREAD_XFL = "67eac6bc-4ea9-11ea-82b5-0e8f358e9391"
POST_FLAIR_GAME_THREAD = _POST_FLAIR_GAME_THREAD_XFL if SUBREDDIT.lower() == "xfl" else _POST_FLAIR_GAME_THREAD_XFLDEV

# Helper functions
def get_sticky_threads():
    stickies = []
    for submission in subreddit.hot(limit=2):
        if submission.stickied:
            stickies.append(submission)
    return stickies
import praw
import re
import stats as stats_api
from dateutil import parser as date_parser
from datetime import datetime, timedelta
from . import *

# Game thread info
GAME_THREAD_LIVE_TAG = "Game Thread:"
GAME_THREAD_FINAL_TAG = "Postgame Thread:"

# Different regex
re_game_id = re.compile(r'http\:\/\/stats\.xfl\.com\/([0-9]+)')

# Team to subreddit mapping
team_reddits = {
    "SEA": "[r/SeattleDragons](https://www.reddit.com/r/SeattleDragons/)",
    "DC": "[r/DCDefenders](https://www.reddit.com/r/DCDefenders/)",
    "TB": "[r/vipers](https://www.reddit.com/r/vipers/)",
    "NY": "[r/NewYorkGuardians](https://www.reddit.com/r/NewYorkGuardians/)",
    "HOU": "[r/Roughnecks/](https://www.reddit.com/r/Roughnecks/)",
    "LA": "[r/lawildcats](https://www.reddit.com/r/lawildcats/)",
    "DAL": "[r/DallasRenegades](https://www.reddit.com/r/DallasRenegades/)",
    "STL": "[r/battlehawks/](https://www.reddit.com/r/battlehawks/)"
}

# Titles
GAME_THREAD_TITLE = GAME_THREAD_LIVE_TAG + " {{HOME_TEAM}} vs. {{AWAY_TEAM}}"
POSTGAME_THREAD_TITLE = GAME_THREAD_FINAL_TAG + \
    " {{WINNER_NAME}} defeat {{LOSER_NAME}}, {{WINNER_SCORE}}-{{LOSER_SCORE}}"

# Post formats
GAME_POST_FORMAT = """
[Box Score](http://stats.xfl.com/{{GameID}}) | Coverage: {{NETWORK}} | [Reddit-Stream]({{STREAM_LINK}}) | {{HOME_REDDIT}} | {{AWAY_REDDIT}} 

---

# Scoring

**Q{{QUARTER}}** - {{CLOCK}} | **{{POSSESION}} Ball** - {{DOWN}} & {{DISTANCE}} w/ Ball at {{BALL_LOCATION}}

{{SCORING_TABLE}}

---

# Last 10 Plays

{{LAST_PLAYS}}

---

- Discuss whatever you wish. You can trash talk, but keep it civil.
- If you are experiencing problems with comment sorting in the official reddit app, we suggest using a third-party client instead (Android, iOS)
- Turning comment sort to 'new' will help you see the newest comments.
- Show your team affiliation - pick your team's logo in the sidebar.

---

Comments / Questions / Complaints? [Message the Moderators](http://www.reddit.com/message/compose?to=%2Fr%2Fxfl)

Connect with us on social media! [Discord](http://www.discord.gg/xfl) | [Twitter](http://www.twitter.com/redditXFL) | [IRC](http://webchat.freenode.net/?channels=reddit-xfl)

"""

POSTGAME_POST_FORMAT = """
[Box Score](http://stats.xfl.com/{{GameID}}) | Coverage: {{NETWORK}} | {{HOME_REDDIT}} | {{AWAY_REDDIT}} 

---
# Scoring

{{SCORING_TABLE}}

---

Comments / Questions / Complaints? [Message the Moderators](http://www.reddit.com/message/compose?to=%2Fr%2Fxfl)

Connect with us on social media! [Discord](http://www.discord.gg/xfl) | [Twitter](http://www.twitter.com/redditXFL) | [IRC](http://webchat.freenode.net/?channels=reddit-xfl)

"""


def _format_game_thread(game_id, post_format=GAME_POST_FORMAT, submission_id=""):
    """
    Format a game thread post with the given stats
    """
    stats = stats_api.get_api_data(game_id)

    text = post_format
    text = text.replace("{{GameID}}", str(game_id))

    # Get game stats
    game_stats = None
    for game in stats["games"]:
        if game["gameId"] == game_id:
            game_stats = game
            break
    if game_stats is None:
        return "Error - No stats found for game id %d" % game_id

    # Team names and IDs
    home_team_name = game_stats["homeTeamName"]
    home_team_abbr = game_stats["homeTeamAbbr"]
    home_team_id = game_stats["homeTeamId"]
    away_team_name = game_stats["awayTeamName"]
    away_team_abbr = game_stats["awayTeamAbbr"]
    away_team_id = game_stats["awayTeamId"]

    # Possesion
    poss = home_team_abbr if game_stats["possessionId"] == home_team_id else away_team_abbr

    # Game stats
    text = text.replace("{{HOME_TEAM_NAME}}", home_team_name)
    text = text.replace("{{AWAY_TEAM_NAME}}", away_team_name)
    text = text.replace("{{QUARTER}}", str(game_stats["gameQuarter"]))
    text = text.replace("{{CLOCK}}", str(game_stats["gameClock"]))
    text = text.replace("{{BALL_LOCATION}}", str(game_stats["ballLocation"]))
    text = text.replace("{{DOWN}}", str(game_stats["playDownFormatted"]))
    text = text.replace("{{DISTANCE}}", str(game_stats["playDistance"]))
    text = text.replace("{{POSSESION}}", poss)
    text = text.replace("{{NETWORK}}", game_stats["network"])
    text = text.replace("{{HOME_REDDIT}}", team_reddits[home_team_abbr])
    text = text.replace("{{AWAY_REDDIT}}", team_reddits[away_team_abbr])
    text = text.replace(
        "{{STREAM_LINK}}", "https://reddit-stream.com/comments/%s/" % submission_id)

    # Scoring
    home_scores = {}
    away_scores = {}
    for q in range(1, 5):
        home_scores[str(q)] = 0
        away_scores[str(q)] = 0

    for play in stats["playList"]["plays"]:

        # Play info
        q = str(play["Quarter"])
        home = play["EndHomeScore"] - play["StartHomeScore"]
        away = play["EndAwayScore"] - play["StartAwayScore"]

        # Points called back on a penalty produce this case
        if home < 0 or away < 0:
            continue

        # Add to dict if OT shows up
        if q not in home_scores:
            home_scores[q] = 0
        if q not in away_scores:
            away_scores[q] = 0

        # Update
        home_scores[q] += home
        away_scores[q] += away

    # Format scoring into table
    quarters = [str(q) for q in home_scores.keys()]
    quarters.sort()

    table_header = ["**Team**"] + ["**%s**" %
                                   q for q in quarters] + ["**Total**"]
    table_alignments = [":-:"] * (len(quarters) + 2)
    table_home_columns = ["**%s**" % home_team_abbr]
    table_away_columns = ["**%s**" % away_team_abbr]
    for q in quarters:
        table_home_columns.append(str(home_scores[q]))
        table_away_columns.append(str(away_scores[q]))
    table_home_columns.append(str(game_stats["homeScore"]))
    table_away_columns.append(str(game_stats["awayScore"]))

    score_table = "|".join(table_header) + "\n"
    score_table += "|".join(table_alignments) + "\n"
    score_table += "|".join(table_home_columns) + "\n"
    score_table += "|".join(table_away_columns) + "\n"

    text = text.replace("{{SCORING_TABLE}}", score_table)

    # Last plays
    plays_table = "Team|Clock|Down & Distance|Play Description\n"
    plays_table += ":--|:--|:--|:--\n"
    last_plays = stats["playList"]["plays"]
    last_plays.reverse()
    for play in last_plays[:10]:
        situation = play["Situation"] if play["Situation"] is not None else ""
        clock = "Q%d - %s" % (play["Quarter"], play["StartTime"])

        plays_table += "|".join([play["ClubCode"], clock, situation,
                                 play["PlayDescription"]]) + "\n"

    text = text.replace("{{LAST_PLAYS}}", plays_table)

    return text


def _get_game_threads():
    """
    Gets all the game threads. Rather than maintain state we
    check for currently active game threads in case they get taken
    down or the bot goes down.
    """

    active_threads = {}
    final_threads = {}

    for submission in redditor.submissions.new(limit=25):
        if submission.subreddit == subreddit:

            # Get game ID
            game_id_s = re_game_id.search(submission.selftext)
            if game_id_s is None:
                continue
            game_id = int(game_id_s.group(1))

            # Determine thread type
            if GAME_THREAD_LIVE_TAG in submission.title:
                active_threads[game_id] = submission
            elif GAME_THREAD_FINAL_TAG in submission.title:
                final_threads[game_id] = submission

    return active_threads, final_threads


def _post_postgame_thread(game):
    """
    Posts a postgame thread for the given game
    """

    # Prevent old posts - Game must be less than a day old
    game_time = date_parser.parse(game["gameStartTimestampUTC"])
    now = datetime.utcnow()
    if game_time + timedelta(hours=24) < now:
        return

    # Get stats
    home_name = game["homeTeamName"]
    home_score = game["homeScore"]
    away_name = game["awayTeamName"]
    away_score = game["awayScore"]

    # Format title
    title = POSTGAME_THREAD_TITLE
    if home_score > away_score:
        title = title.replace("{{WINNER_NAME}}", home_name)
        title = title.replace("{{WINNER_SCORE}}", str(home_score))
        title = title.replace("{{LOSER_NAME}}", away_name)
        title = title.replace("{{LOSER_SCORE}}", str(away_score))
    else:
        title = title.replace("{{WINNER_NAME}}", away_name)
        title = title.replace("{{WINNER_SCORE}}", str(away_score))
        title = title.replace("{{LOSER_NAME}}", home_name)
        title = title.replace("{{LOSER_SCORE}}", str(home_score))

    # Submit post
    print("Posting: %s" % title)
    submission = subreddit.submit(
        title=title,
        selftext=_format_game_thread(
            game["gameId"], post_format=POSTGAME_POST_FORMAT),
        send_replies=False,
        flair_id='game-thread-2')
    submission.mod.distinguish()


def _post_game_thread(game):
    """
    Posts a game thread for the given game
    """

    # Prevent old and too new posts - Game must be within the next 2 hours, but also not already started
    game_time = date_parser.parse(game["gameStartTimestampUTC"])
    now = datetime.utcnow() - timedelta(hours=32)
    if game_time - timedelta(hours=2) > now or game_time < now:
        return

    # Get stats
    home_name = game["homeTeamName"]
    away_name = game["awayTeamName"]

    # Format title
    title = GAME_THREAD_TITLE
    title = title.replace("{{HOME_TEAM}}", home_name)
    title = title.replace("{{AWAY_TEAM}}", away_name)

    # Submit post
    print("Posting: %s" % title)
    submission = subreddit.submit(
        title=title,
        selftext=_format_game_thread(game["gameId"]),
        send_replies=False,
        flair_id='game-thread-1')
    submission.mod.suggested_sort("new")
    submission.mod.distinguish()


def update_games():
    """
    Update the current game threads
    """

    active_threads, final_threads = _get_game_threads()
    api_data = stats_api.get_api_data()

    # Check for new game threads to post
    for game in api_data["games"]:
        if game["isGameOver"]:
            continue
        if game["gameId"] not in active_threads:
            _post_game_thread(game)
        else:
            submission = active_threads[game["gameId"]]
            print("Updating: %s" % submission.title)
            submission.edit(_format_game_thread(
                game["gameId"], submission_id=submission.id))

    # Check for final threads to post
    for game in api_data["games"]:
        if game["isGameOver"] and game["gameId"] not in final_threads:
            _post_postgame_thread(game)

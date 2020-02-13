import praw
import json
from . import *
from textblob import TextBlob
import matplotlib.pyplot as plt


def run():
    submission = reddit.submission(id='f0v1s6')
    # submission.comments.replace_more(limit=None)

    team1 = "defenders"
    team2 = "dragons"

    team1Times, team1Polarities = [], []
    team2Times, team2Polarities = [], []
    otherTimes, otherPolarities = [], []

    print(len(submission.comments.list()))

    for comment in submission.comments.list():
        if isinstance(comment, praw.models.MoreComments):
            continue
        text = TextBlob(comment.body)
        polarity = text.polarity
        time = comment.created_utc
        flair = comment.author_flair_css_class

        if flair == team1:
            team1Times.append(time)
            team1Polarities.append(polarity)
        elif flair == team2:
            team2Times.append(time)
            team2Polarities.append(polarity)
        else:
            otherTimes.append(time)
            otherPolarities.append(polarity)

    otherTimesSorted = [x for x, _ in sorted(zip(otherTimes, otherPolarities))]
    otherPolaritiesSorted = [x for _, x in sorted(
        zip(otherTimes, otherPolarities))]

    team1TimesSorted = [x for x, _ in sorted(zip(team1Times, team1Polarities))]
    team1PolaritiesSorted = [x for _, x in sorted(
        zip(team1Times, team1Polarities))]

    team2TimesSorted = [x for x, _ in sorted(zip(team2Times, team2Polarities))]
    team2PolaritiesSorted = [x for _, x in sorted(
        zip(team2Times, team2Polarities))]

    with open('other.json', 'w') as outfile:
        json.dump(list(zip(otherTimesSorted, otherPolaritiesSorted)), outfile)

    with open('team1.json', 'w') as outfile:
        json.dump(list(zip(team1TimesSorted, team1PolaritiesSorted)), outfile)

    with open('team2.json', 'w') as outfile:
        json.dump(list(zip(team2TimesSorted, team2PolaritiesSorted)), outfile)

    plt.plot(otherTimesSorted, otherPolaritiesSorted)
    plt.plot(team1TimesSorted, team1PolaritiesSorted)
    plt.plot(team2TimesSorted, team2PolaritiesSorted)
    plt.show()

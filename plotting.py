import json
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import matplotlib.dates as mdates

from scipy.interpolate import spline
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter

from datetime import datetime
from datetime import timedelta
from dateutil import parser as date_parser

from utils.stats import get_api_data

api_data = get_api_data()
game = api_data["games"][0]

game_start = date_parser.parse(game["gameStartTimestampUTC"])
game_end = game_start + timedelta(hours=4)

SCORING_PLAYS = {"Touchdown": "%s TD",
                 "Field Goal": "%s FG",
                 "Interception": "%s INT6",
                 "Fumble": "%s FR6"}


def get_important_times(game, plays):

    times, labels = [], []

    # Check all plays for points of interest
    for _, play in enumerate(plays):

        # Scoring plays
        if play["playScoreType"] in SCORING_PLAYS.keys():

            # Compute times and labels
            time = date_parser.parse(play["StartTime"])
            minutes = int(play["StartTime"].split(":")[0])
            seconds = int(play["StartTime"].split(":")[1])
            label = SCORING_PLAYS[play["playScoreType"]] % play["ClubCode"]

            # Calculate time with offset
            offset = timedelta(minutes=15) * (play["Quarter"] - 1) + \
                (timedelta(minutes=15) -
                 timedelta(minutes=minutes, seconds=seconds))
            time = game_start + offset
            print(offset)

            times.append(time)
            labels.append(label)

    return times, labels


def add_to_plot(fig, x, y, color, label):
    xx = np.linspace(x.min(), x.max(), 1000)
    itp = interp1d(x, y, kind='linear')
    window_size, poly_order = 101, 3
    yy = savgol_filter(itp(xx), window_size, poly_order)

    xx_dt = [datetime.utcfromtimestamp(x) for x in xx]
    dates = matplotlib.dates.date2num(xx_dt)

    fig.plot_date(dates, yy, color, linewidth=3, label=label)


# Create a canvas to place the subgraphs
canvas = plt.figure()
rect = canvas.patch
rect.set_facecolor('white')
fig = canvas.subplots()

# Axis formatting
myFmt = mdates.DateFormatter('%H:%M')
fig.xaxis.set_major_formatter(myFmt)
trans = transforms.blended_transform_factory(
    fig.axes.transData, fig.axes.transAxes)

# Put the title and labels
fig.set_title('STL v DC')
fig.set_xlabel('Game Time')
fig.set_ylabel('Fanbase Sentiment')

with open('team1.json') as json_file:
    data = json.load(json_file)
x = np.array([x for x, _ in data if datetime.utcfromtimestamp(
    x) > game_start and datetime.utcfromtimestamp(x) < game_end])
y = np.array([y for x, y in data if datetime.utcfromtimestamp(
    x) > game_start and datetime.utcfromtimestamp(x) < game_end])
add_to_plot(fig, x, y, 'black', 'DC')

with open('team2.json') as json_file:
    data = json.load(json_file)
x = np.array([x for x, _ in data if datetime.utcfromtimestamp(
    x) > game_start and datetime.utcfromtimestamp(x) < game_end])
y = np.array([y for x, y in data if datetime.utcfromtimestamp(
    x) > game_start and datetime.utcfromtimestamp(x) < game_end])
add_to_plot(fig, x, y, 'red', 'STL')

# Add important points
times, labels = get_important_times(game, api_data["playList"]["plays"])

for time, label in zip(times, labels):
    print(time, label)
    plt.axvline(time)
    plt.text(time, +0.1, label, transform=trans)

# Show the plot/image
plt.legend(loc="upper left")
plt.tight_layout()
plt.grid(alpha=0.8)
plt.show()

import json
import matplotlib
import matplotlib.pyplot as plt
from scipy.interpolate import spline
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates
from datetime import timedelta
from stats import get_api_data
from dateutil import parser as date_parser

api_data = get_api_data()

game_time = date_parser.parse(api_data["gameStartTimestampUTC"])
game_start = datetime.utcfromtimestamp(1581184854.0)
game_end = game_start + timedelta(hours=5)


def add_to_plot(sp1, x, y, color, label):
    xx = np.linspace(x.min(), x.max(), 1000)
    itp = interp1d(x, y, kind='linear')
    window_size, poly_order = 101, 3
    yy = savgol_filter(itp(xx), window_size, poly_order)

    xx_dt = [datetime.utcfromtimestamp(x) for x in xx]
    dates = matplotlib.dates.date2num(xx_dt)

    sp1.plot_date(dates, yy, color, linewidth=3, label=label)


# Create a canvas to place the subgraphs
canvas = plt.figure()
rect = canvas.patch
rect.set_facecolor('white')

# Define the matrix of 1x1 to place subplots
# Placing the plot1 on 1x1 matrix, at pos 1
sp1 = canvas.add_subplot(1, 1, 1)

# Put the title and labels
sp1.set_title('STL v DC')
sp1.set_xlabel('Game Time')
sp1.set_ylabel('Fanbase Sentiment')

myFmt = mdates.DateFormatter('%H:%M')
sp1.xaxis.set_major_formatter(myFmt)

with open('team1.json') as json_file:
    data = json.load(json_file)
x = np.array([x for x, _ in data if datetime.utcfromtimestamp(
    x) > game_start and datetime.utcfromtimestamp(x) < game_end])
y = np.array([y for x, y in data if datetime.utcfromtimestamp(
    x) > game_start and datetime.utcfromtimestamp(x) < game_end])
add_to_plot(sp1, x, y, 'black', 'DC')

with open('team2.json') as json_file:
    data = json.load(json_file)
x = np.array([x for x, _ in data if datetime.utcfromtimestamp(
    x) > game_start and datetime.utcfromtimestamp(x) < game_end])
y = np.array([y for x, y in data if datetime.utcfromtimestamp(
    x) > game_start and datetime.utcfromtimestamp(x) < game_end])
add_to_plot(sp1, x, y, 'red', 'STL')

with open('other.json') as json_file:
    data = json.load(json_file)
x = np.array([x for x, _ in data if datetime.utcfromtimestamp(
    x) > game_start and datetime.utcfromtimestamp(x) < game_end])
y = np.array([y for x, y in data if datetime.utcfromtimestamp(
    x) > game_start and datetime.utcfromtimestamp(x) < game_end])
# add_to_plot(sp1, x, y, 'green')

# Show the plot/image
plt.legend(loc="upper left")
plt.tight_layout()
plt.grid(alpha=0.8)
plt.show()

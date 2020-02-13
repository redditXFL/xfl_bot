import time
import bots
from utils import stats

while True:
    bots.games.update_games()
    time.sleep(30)

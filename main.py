import time
from bots import games as game_bot
from utils import stats

while True:
    game_bot.update_games()
    time.sleep(30)

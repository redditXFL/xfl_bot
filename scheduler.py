import time
from datetime import datetime, timedelta
from threading import Thread

from bots import games as game_bot

# Schedule for running tasks
# Format:
#   name: Name of task
#   function: Function pointer
#   args: Arguments (if any)
#   interval: Interval to run at
SCHEDULE = [
    {
        "name": "Game Thread Updater"
        "function": game_bot.update_games,
        "args": (),
        "interval": timedelta(seconds=30)
    },
]

# Loop forever, every 1 second
while True:
    time.sleep(1)

    # Check tasks in schedule
    for task in SCHEDULE:

        # Add last_run tracker
        if "last_run" not in task:
            task["last_run"] = datetime.now()

        # Check if its time to run, if so run
        if task["last_run"] + task["interval"] < datetime.now():
            print("Running Task:", task["name"], datetime.now())
            Thread(target=task["function"], args=task["args"]).start()
            task["last_run"] = datetime.now()
        

    

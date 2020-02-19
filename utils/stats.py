import requests
import json, csv
import re
from bs4 import BeautifulSoup
from collections import OrderedDict

URL = 'http://stats.xfl.com/'


def get_api_data(game_id=1):
    """
    Here we scrape the API data from the XFL's site. They embed their API call data directly into
    the webpage so we don't need an API key.
    """
    page = requests.get(URL + str(game_id))

    soup = BeautifulSoup(page.content, 'html.parser')
    html_api_data = soup.findAll("script")

    # Store the api data to return
    api_data = {}

    re_var_name = re.compile(r'var\s([\w+]+)\s=')
    for js in html_api_data:
        js = js.text

        # Check for variable name
        s = re_var_name.search(js)
        if s is None:
            continue
        var_name = s.group(1)

        # Save data as json
        try:
            api_data[var_name] = json.loads(js.split("=")[1].replace(";", ""), object_pairs_hook=OrderedDict)
        except:
            pass  # We probably just found a false positive

    return api_data

def stats_as_csv(game_id=1):
    """
    Gets the stats for a game as a CSV
    """

    data = get_api_data(game_id)
    with open("data.json", "w+") as f:
        json.dump(data, f, indent=2)

    home_team = data["games"][game_id]["homeTeamAbbr"]
    away_team = data["games"][game_id]["awayTeamAbbr"]
    prefix = away_team + "_" + home_team

    # Team Total Stats
    f = csv.writer(open(prefix + "_team.csv", "w+"))

    headers = ["TeamName"] + list(data["teamStats"]["awayStats"]["stats"].keys())
    away = [away_team] + list(data["teamStats"]["awayStats"]["stats"].values())
    home = [home_team] + list(data["teamStats"]["homeStats"]["stats"].values())

    f.writerow(headers)
    f.writerow(away)
    f.writerow(home)

    def get_team_stat(csv, stats, statData, team, teamName):

        players = []
        for _, stat in enumerate(stats):
            players += [entry["player"]["id"] for entry in statData[team][stat]]
            players += [entry["player"]["id"] for entry in statData[team][stat]]
            players += [entry["player"]["id"] for entry in statData[team][stat]]
        players = set(players)

        player_data = {}
        for player in players:
            player_data[player] = {}
            for key in headers:
                player_data[player][key] = 0

        for _, stat in enumerate(stats):
            for entry in statData[team][stat]:
                id = entry["player"]["id"]
                player_data[id]["TeamName"] = teamName
                player_data[id]["PlayerName"] = entry["player"]["displayName"]
                player_data[id]["PlayerNumber"] = entry["player"]["jerseyNumber"]
                del entry["player"]
                for key in entry.keys():
                    player_data[id][stat.capitalize() + key.capitalize()] = entry[key]

        out = []
        for player in players:
            pdata = []
            for _, key in enumerate(headers):
                pdata += [player_data[player][key]]
            out += [pdata]
        csv.writerows(out)

    # Offensive stats
    f = csv.writer(open(prefix + "_offense.csv", "w+"))

    rushing_headers = list(data["offensiveStats"]["away"]["rushing"][0].keys())
    passing_headers = list(data["offensiveStats"]["away"]["passing"][0].keys())
    receiving_headers = list(data["offensiveStats"]["away"]["receiving"][0].keys())

    headers = ["TeamName", "PlayerName", "PlayerNumber"]
    headers += ["Rushing" + k.capitalize() for k in rushing_headers]
    headers += ["Passing" + k.capitalize() for k in passing_headers]
    headers += ["Receiving" + k.capitalize() for k in receiving_headers]
    headers.remove("RushingPlayer")
    headers.remove("PassingPlayer")
    headers.remove("ReceivingPlayer")

    f.writerow(headers)
    get_team_stat(f, ["rushing", "passing", "receiving"], data["offensiveStats"], "away", away_team)
    get_team_stat(f, ["rushing", "passing", "receiving"], data["offensiveStats"], "home", home_team)

    # Defensive stats
    f = csv.writer(open(prefix + "_defense.csv", "w+"))

    defensive_headers = list(data["defensiveStats"]["away"]["defensive"][0].keys())

    headers = ["TeamName", "PlayerName", "PlayerNumber"]
    headers += ["Defensive" + k.capitalize() for k in defensive_headers]
    headers.remove("DefensivePlayer")

    f.writerow(headers)
    get_team_stat(f, ["defensive"], data["defensiveStats"], "away", away_team)
    get_team_stat(f, ["defensive"], data["defensiveStats"], "home", home_team)

    # Plays
    f = csv.writer(open(prefix + "_plays.csv", "w+"))

    headers = list(data["playList"]["plays"][0].keys())
    f.writerow(headers)

    for play in data["playList"]["plays"]:
        f.writerow(list(play.values()))

    # Possessions
    f = csv.writer(open(prefix + "_possessions.csv", "w+"))

    headers = list(data["possessionStats"]["away"]["possessions"][0].keys())
    f.writerow(headers)

    for poss in data["possessionStats"]["away"]["possessions"] + data["possessionStats"]["home"]["possessions"]:
        f.writerow(list(poss.values()))



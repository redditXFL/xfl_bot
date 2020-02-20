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

    games = {}
    for game in data["games"]:
        games[game["gameId"]] = game
    if (game_id not in games) or (not games[game_id]["isGameOver"]):
        print((game_id not in games), (not games[game_id]["isGameOver"]))
        return None

    home_team = games[game_id]["homeTeamAbbr"]
    away_team = games[game_id]["awayTeamAbbr"]
    prefix = away_team + "_" + home_team

    # Team Total Stats
    tt_headers = ["GameID", "TeamName"] + list(data["teamStats"]["awayStats"]["stats"].keys())
    tt_away = [game_id, away_team] + list(data["teamStats"]["awayStats"]["stats"].values())
    tt_home = [game_id, home_team] + list(data["teamStats"]["homeStats"]["stats"].values())

    def get_team_stat(csv, stats, statData, team, teamName):

        headers = ["TeamName", "PlayerName", "PlayerNumber"]
        players = []
        for _, stat in enumerate(stats):
            players += [entry["player"]["id"] for entry in statData[team][stat]]
            headers += [stat.capitalize() + key.capitalize() for key in statData[team][stat][0].keys()]
            headers.remove(stat.capitalize() + "Player")
        
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
            pdata = [game_id]
            for _, key in enumerate(headers):
                pdata += [player_data[player][key]]
            out += [pdata]
        return out

    # Offensive stats
    rushing_headers = list(data["offensiveStats"]["away"]["rushing"][0].keys())
    passing_headers = list(data["offensiveStats"]["away"]["passing"][0].keys())
    receiving_headers = list(data["offensiveStats"]["away"]["receiving"][0].keys())

    o_headers = ["GameID", "TeamName", "PlayerName", "PlayerNumber"]
    o_headers += ["Rushing" + k.capitalize() for k in rushing_headers]
    o_headers += ["Passing" + k.capitalize() for k in passing_headers]
    o_headers += ["Receiving" + k.capitalize() for k in receiving_headers]
    o_headers.remove("RushingPlayer")
    o_headers.remove("PassingPlayer")
    o_headers.remove("ReceivingPlayer")

    o_away = get_team_stat(f, ["rushing", "passing", "receiving"], data["offensiveStats"], "away", away_team)
    o_home = get_team_stat(f, ["rushing", "passing", "receiving"], data["offensiveStats"], "home", home_team)

    # Defensive stats
    defensive_headers = list(data["defensiveStats"]["away"]["defensive"][0].keys())

    d_headers = ["GameID", "TeamName", "PlayerName", "PlayerNumber"]
    d_headers += ["Defensive" + k.capitalize() for k in defensive_headers]
    d_headers.remove("DefensivePlayer")

    d_away = get_team_stat(f, ["defensive"], data["defensiveStats"], "away", away_team)
    d_home = get_team_stat(f, ["defensive"], data["defensiveStats"], "home", home_team)

    # Plays
    p_headers = ["GameID"] + list(data["playList"]["plays"][0].keys())

    p_rows = []
    for play in data["playList"]["plays"]:
        p_rows.append([game_id] + list(play.values()))

    # Possessions
    po_headers = ["GameID"] + list(data["possessionStats"]["away"]["possessions"][0].keys())

    po_rows = []
    for poss in data["possessionStats"]["away"]["possessions"] + data["possessionStats"]["home"]["possessions"]:
        po_rows.append([game_id] + list(poss.values()))

    return (tt_headers, [tt_away] + [tt_home]), (o_headers, o_away + o_home), (d_headers, d_away + d_home), (p_headers, p_rows), (po_headers, po_rows)



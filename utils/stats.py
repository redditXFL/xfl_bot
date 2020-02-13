import requests
import json
import re
from bs4 import BeautifulSoup

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
            api_data[var_name] = json.loads(js.split("=")[1].replace(";", ""))
        except:
            pass  # We probably just found a false positive

    return api_data

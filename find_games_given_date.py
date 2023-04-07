# Copyright (C) 2023 Warren Usui, MIT License
"""
Given a date, return list of boxscores
"""
from datetime import datetime
from datetime import timedelta
import requests
from bs4 import BeautifulSoup

def get_gdate(date_v):
    """
    Link date with scoreboard
    """
    return "/".join(["https://www.cbssports.com/mlb/scoreboard",
                      f"{date_v.strftime('%Y%m%d')}", ""])

def get_req(date_v):
    """
    Read a url
    """
    return requests.get(get_gdate(date_v), timeout=600).text

def get_soup(date_v):
    """
    Get the scoreboard with links to boxscores
    """
    return BeautifulSoup(get_req(date_v), "html.parser")

def get_gameinfo(date_v):
    """
    Extract game links
    """
    return get_soup(date_v).find_all("a", href=True)

def get_games(date_v):
    """
    Scan game page for this day
    """
    return list(filter(lambda a: a.attrs['href'].startswith(
            '/mlb/gametracker/boxscore/'), get_gameinfo(date_v)))

def msnp_req(url_v):
    """
    Read url (checking for postponed games)
    """
    return requests.get("https://www.cbssports.com" + url_v,
                timeout=600).text

def msnp_bs(url_v):
    """
    Get Beautiful Soup data (checking for postponed games)
    """
    return BeautifulSoup(msnp_req(url_v), "html.parser")

def msnp_find_hrefs(url_v):
    """
    Get hrefs (checking for postponed games)
    """
    return msnp_bs(url_v).find_all("a", href=True)

def msnp_find_pp(url_v):
    """
    Postponed games are determined by having too few player references
    """
    return list(filter(lambda a: "playerpage" in a.attrs['href'],
                      msnp_find_hrefs(url_v)))

def make_sure_not_postponed(url_v):
    """
    Remove postponed games from list
    """
    if len(msnp_find_pp(url_v)) > 18:
        return True
    return False

def find_games_on_date(date_v):
    """
    Return extracted boxscore links
    """
    return list(filter(make_sure_not_postponed,
            list(map(lambda a: a.attrs['href'], get_games(date_v)))))

def find_games_given_date(date_str):
    """
    Date_str in YYYYmmdd format
    """
    return find_games_on_date(datetime.strptime(date_str, "%Y%m%d"))

def find_yesterdays_games():
    """
    Called by update_day_records
    """
    return find_games_on_date(datetime.now() - timedelta(days=1))

if __name__ == "__main__":
    print(find_yesterdays_games())
    print(find_games_given_date("20230330"))

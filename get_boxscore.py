# Copyright (C) 2023 Warren Usui, MIT License
"""
Extract boxscore data (data will be sorted out by parse_boxscore)
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_ppage_links(ahref_clause):
    """
    Extract player page link
    """
    if "playerpage" in ahref_clause['href']:
        return ahref_clause['href']
    return ' '

def get_player_links(soup):
    """
    Extract player page links for all players
    """
    return list(set(list(map(get_ppage_links, soup.find_all("a", href=True)))))

def id_filter_non_links(string_list):
    """
    Filter out non-id links
    """
    return list(filter(lambda a: a.startswith("https"), string_list))

def get_sb_info(soup):
    """
    Extract stolen base text
    """
    def psi_2():
        return soup.find_all('div', class_='gametracker-panel')
    def psi_1():
        return list(map(lambda a: a.text, psi_2()))
    return list(filter(lambda a: a.startswith('BASERUNNING'), psi_1()))

def get_sb_headers(soup):
    """
    Scan stolen base headers to determine team if only one team stole bases
    """
    return list(soup.find_all("div",
                class_="gametracker-panel--always-show-desktop")[6].children)

def get_scrape_info(req_text):
    """
    Scrape the player list and stolen base information
    """
    def gsi_inner(soup):
        return [["players", id_filter_non_links(get_player_links(soup))],
                ["sb_info", get_sb_info(soup)],
                ["sb_headers", get_sb_headers(soup)]]
    return gsi_inner(BeautifulSoup(req_text, "html.parser"))

def get_tables(url_name):
    """
    Extract the main tables as dataframes
    """
    def gt_inner(pd_info):
        return list(map(lambda a: pd_info[a], list(range(1,9,2))))
    return [["tables", gt_inner(pd.read_html(url_name))]]

def extract_team_info(url_name):
    """
    Extract the abbreviations for the teams playing
    """
    return list(filter(lambda a: a, url_name.split('/')))[-1]

def get_boxscore(url_v):
    """
    Extract boxscore data (results will be used by parse_boxscore)
    """
    return dict([['game_info', extract_team_info(url_v)]] +
            get_scrape_info(requests.get(url_v, timeout=600).text) +
            get_tables(url_v))

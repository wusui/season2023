# Copyright (C) 2023 Warren Usui, MIT License
"""
Create abbrev -> full team name json and full team name -> abbrev json
"""
import os
import json
from oldies.common import get_soup

def fix_name(ntext):
    """
    Reformat "chicago-white-sox" to "Chicago White Sox"
    """
    return " ".join(list(map(lambda a: a.capitalize(), ntext.split('-'))))

def split_data(team_info):
    """
    Return [abbreviation, team name]
    """
    return [team_info[3], fix_name(team_info[4])]

def parse_team(fline):
    """
    Find singular (stats) use of team name link for each team)
    """
    if fline['href'].startswith("/mlb/teams/"):
        if fline['href'].endswith("stats/"):
            return split_data(fline['href'].split("/"))
    return []

def scan_teams(soup):
    """
    Extract fields with <a> tags and href attributes
    """
    return list(map(parse_team, soup.find_all("a", href=True)))

def collect_data():
    """
    Read team name from web.
    """
    return scan_teams(get_soup("https://www.cbssports.com/mlb/teams/"))

def clean_data(in_data):
    """
    Remove empty entries from list
    """
    return list(filter(lambda a: a, in_data))

def get_mlb_teams():
    """
    Collect data, grab only AL part, make dict
    """
    return dict(clean_data(collect_data())[0:15])

def lflip(t_info):
    """
    Flip a single {abbrev: team_name} entry
    """
    def lflip_inner(info_line):
        return [t_info[info_line], info_line]
    return lflip_inner

def flip(t_info):
    """
    Create dict of flipped value: Key entries
    """
    return dict(list(map(lflip(t_info), list(t_info))))

def sv_mlb_teams(t_info):
    """
    Stash mlb team name and abbreviation data into two files.
    """
    def do_dump(ofile):
        def do_dump_inner(data_dict):
            with open(os.sep.join(["data", ofile]), 'w',
                      encoding='utf-8') as ofd:
                json.dump(data_dict, ofd)
        return do_dump_inner
    do_dump("teams.json")(t_info)
    do_dump("abbrevs.json")(flip(t_info))

def save_mlb_teams():
    """
    Do computations (in get_mlb_teams) and pass to output routine
    """
    sv_mlb_teams(get_mlb_teams())

if __name__ == "__main__":
    save_mlb_teams()

# Copyright (C) 2023 Warren Usui, MIT License
"""
Stash data in json file
"""
import os
import json
from datetime import datetime
from datetime import timedelta
import pandas as pd
from parse_boxscore import parse_boxscore
from find_games_given_date import find_yesterdays_games

def get_bandp(yesterdays_list):
    """
    Convert pandas data into one dict containing a batter list and
    a pitcher list
    """
    def xtrct(pos_no):
        return pd.concat(list(map(lambda a: a[pos_no],
                              yesterdays_list)), ignore_index=True)
    return {'batters': list(xtrct(0).transpose().to_dict().values()),
            'pitchers': list(xtrct(1).transpose().to_dict().values())}

def get_big_dict():
    """
    Generate a dictionary of all players who played on a given day
    """
    return get_bandp(list(map(parse_boxscore, find_yesterdays_games())))

def get_yday():
    """
    Get yesterday's date
    """
    return datetime.now() - timedelta(days=1)

def get_fname():
    """
    Generate name of output file
    """
    return os.sep.join(['results', f'{get_yday().strftime("%Y%m%d")}.json'])

def update_day_records():
    """
    Save day's results as a json file
    """
    with open(get_fname(), 'w', encoding='utf-8') as outf:
        json.dump(get_big_dict(), outf)

if __name__ == "__main__":
    update_day_records()

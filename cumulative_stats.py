# Copyright (C) 2023 Warren Usui, MIT License
"""
Get all players from the regular season stats page
"""
import os
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd

def gen_url(position):
    """
    Get url for batters/pitchers (with multiple page numbers possible)
    """
    def inner_gen_url(pg_no):
        return "/".join(["https://www.cbssports.com/mlb/stats/player",
                         f"{position}/mlb/regular/all-pos/all",
                         f"?page={pg_no}"])
    return inner_gen_url

def get_soup_fields(url):
    """
    Extract soup result sets containing full player name information
    """
    def iget_soup():
        return BeautifulSoup(requests.get(url, timeout=600).text,
                             "html.parser")
    def iget_tags():
        return iget_soup().find_all(class_="CellPlayerName--long")
    return list(map(lambda a: a.find_all("a", href=True), iget_tags()))

def extract_page(position):
    """
    Extract the ids (found using soup) and pandas tables for all pages
    """
    def in_extract(pg_no):
        def curry_url(url):
            def curry_soup(soup_fields):
                def curry_table(pd_info):
                    def make_record(indx):
                        return [soup_fields[indx][0]['href'], pd_info[indx]]
                    def process_data():
                        return list(map(make_record, range(len(soup_fields))))
                    return process_data() + extract_page(position)(pg_no + 1)
                if not soup_fields:
                    return []
                return curry_table(pd.read_html(url)[0].transpose().to_dict())
            return curry_soup(get_soup_fields(url))
        return curry_url(gen_url(position)(pg_no))
    return in_extract

def cumulative_stats():
    """
    Return stats for both batters and pitchers
    """
    def pos_stats(position):
        return extract_page(position)(1)
    return {"batting": dict(pos_stats("batting")),
            "pitching": dict(pos_stats("pitching"))}

def stash_result():
    """
    Save cummulative results in a json file
    """
    with open(os.sep.join(['results', 'all_stats.json']), 'w',
              encoding='utf-8') as outf:
        json.dump(cumulative_stats(), outf)

if __name__ == "__main__":
    stash_result()

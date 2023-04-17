# Copyright (C) 2023 Warren Usui, MIT License
"""
Find duplicate player names when names are formatted as first initial
followed by the last name
"""
import requests
from bs4 import BeautifulSoup

def read_plyrs(position):
    """
    Extract the data from cbs websites for position (batting and pitching)
    """
    def read_pages(page_no):
        def test_info(p_list):
            if not p_list:
                return p_list
            return p_list + read_pages(page_no + 1)
        def get_soup(page):
            return BeautifulSoup(requests.get(page, timeout=600).text,
                                 "html.parser")
        def get_page():
            return "https://www.cbssports.com/mlb/stats/player/" + \
                f"{position}/al/regular/all-pos/all/?page={page_no}"
        def parse_it(in_soup):
            def get_players(pdata):
                return pdata['href'].startswith('/mlb/players/')
            def rm_extra():
                return in_soup.find_all("a", href=True)
            def rm_non_pl():
                return list(filter(get_players, rm_extra()))
            def rm_empties(plyr_ref):
                return len(plyr_ref['href']) > 13
            return test_info(list(filter(rm_empties, rm_non_pl())))
        def gen_info():
            return parse_it(get_soup(get_page()))
        return test_info(gen_info())
    def extract_href(p_soup):
        return list(map(lambda a: a['href'], p_soup))
    return list(set(extract_href(read_pages(1))))

def find_dup_ids():
    """
    Main entry point -- Find all duplicate names
    """
    def add_parts(two_lists):
        return list(set(two_lists[0] + two_lists[1]))
    def get_all_player_ids():
        return add_parts(list(map(read_plyrs, ["batting", "pitching"])))
    def num_ids(p_list):
        return list(map(lambda a: a.split("/")[-3], p_list))
    def set_nm_prts(fandl):
        return fandl[0][0].capitalize() + ". " + fandl[1].capitalize()
    def fi_sn_orig(entry):
        def fso_inner(name):
            return [set_nm_prts(name.split("-")), name]
        return fso_inner(entry.split("/")[-2])
    def first_initial_surname(p_list):
        return list(map(fi_sn_orig, p_list))
    def find_all_ids(p_list):
        return dict(list(zip(num_ids(p_list), first_initial_surname(p_list))))
    def find_ids_and_names():
        return find_all_ids(get_all_player_ids())
    def sort_player_names(names):
        return sorted(list(map(lambda a: names[a][0], names)))
    def get_player_names():
        return sort_player_names(find_ids_and_names())
    def gen_cmp_pairs(pnames):
        return list(zip(pnames[0:-1], pnames[1:]))
    def get_name_pairs():
        return gen_cmp_pairs(get_player_names())
    def compare_pairs():
        return list(filter(lambda a: a[0] == a[1], get_name_pairs()))
    def find_double_ids(double_answer):
        return list(map(lambda a: a[0], double_answer))
    return find_double_ids(compare_pairs())

if __name__ == "__main__":
    print(find_dup_ids())

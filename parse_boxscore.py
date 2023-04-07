# Copyright (C) 2023 Warren Usui, MIT License
"""
Parse a boxscore
"""
from datetime import datetime
import pandas as pd
from get_boxscore import get_boxscore

def get_game_d(info):
    """
    Get date and team abbrev info for this game.
    """
    return {'date': datetime.strptime(info[-2],
                    '%Y%m%d').strftime("%m/%d/%Y"),
            'teams': info[-1].split('@')}

def get_game_info(date_and_teams):
    """
    Wraper for get_game_d
    """
    return get_game_d(date_and_teams.split("_"))

def gen_pname(nparts):
    """
    Return name as First initial Last name
    """
    return ''.join([nparts[0][0], '. ', nparts[1]])

def gen_name_and_key(player):
    """
    Get Name and key value
    """
    return [gen_pname(player.split('/')[-2].split('-')), player]

def gen_save_value(txt):
    """
    Record any saves
    """
    if "(S" in txt:
        return 1
    return 0

def gen_win_value(txt):
    """
    Identify the winnning pitcher
    """
    if "(W" in txt:
        return 1
    return 0

def get_pit_name(name):
    """
    Extract the name of the pitcher (without W/L/S info
    """
    def get_pit_name2(iname):
        return iname[0:iname.find('(')].strip()
    return get_pit_name2(name + ' ')

def get_bat_pos(name):
    """
    Get the position of the player
    """
    return name.split(" ")[-1]

def rm_ph_head(name):
    """
    Remove excess pinch hitter info from the boxscore
    """
    if name.split(" ")[0].endswith("-"):
        return " ".join(name.split(" ")[1:])
    return name

def get_bat_name(name):
    """
    Piece of code to extract the player name (split from position
    """
    return " ".join(rm_ph_head(name).split(" ")[0:-1])

def do_parse_boxscore(raw_data):
    """
    Main parser for boxscores.
    """
    def pbox_inner(g_info):
        def add_common(df_porb_plus):
            def get_porb_data():
                return df_porb_plus[0].assign(
                        TEAM=g_info['teams'][df_porb_plus[1]])
            return get_porb_data().assign(DATE=g_info['date'])
        def do_bat(indx):
            def get_bat_sb(name):
                def get_sindx():
                    if len(raw_data['sb_info']) == 1:
                        return 0
                    return indx
                def get_pers():
                    return " ".join(name.split(" ")[:-1])
                def sb_count(splt):
                    if len(splt) == 1:
                        return 0
                    if len(splt[1]) == 0:
                        return 1
                    if not splt[1][0].isdigit():
                        return 1
                    return int(splt[1][0])
                def sb_chk_value():
                    return sb_count(
                        raw_data['sb_info'][get_sindx()].split(get_pers()))
                if len(raw_data['sb_info']) == 0:
                    return 0
                if len(raw_data['sb_info']) == 2:
                    return sb_chk_value()
                if indx == 1 and len(raw_data['sb_headers']) == 0:
                    return sb_chk_value()
                if indx == 0 and len(raw_data['sb_headers']) != 0:
                    return sb_chk_value()
                return 0
            def fix_bat(bat_df):
                def get_batname():
                    return bat_df.assign(NAME=bat_df['HITTERS'].apply(
                                    get_bat_name))
                def top_of_bats(bat1):
                    def get_pos():
                        return bat1.assign(POS=bat1['HITTERS'].apply(
                                            get_bat_pos))
                    def get_sb(pre_sb):
                        return pre_sb.assign(SB=bat1['HITTERS'].apply(
                                            get_bat_sb))
                    return add_common([get_sb(get_pos()), indx])
                return top_of_bats(get_batname())
            return fix_bat(raw_data['tables'][indx])
        def get_bat_stats():
            return list(map(do_bat, list(range(0,2))))
        def do_pit(indx):
            def fix_pit(pit_df):
                def pit1(prev):
                    return prev.assign(WH=lambda a: a.H + a.BB)
                def pit2(prev):
                    return prev.assign(WINS=prev['PITCHERS'].apply(
                                gen_win_value))
                def pit3(prev):
                    return prev.assign(SAVES=prev['PITCHERS'].apply(
                                gen_save_value))
                def pit4(prev):
                    return prev.assign(NAME=prev['PITCHERS'].apply(
                                get_pit_name))
                def pit5(prev):
                    return prev.assign(OUTS=prev['IP'].apply(
                                lambda a : int(a * 3) + (a * 10) % 10))
                return add_common([pit1(pit2(pit3(pit4(pit5(pit_df))))),
                                   indx - 2])
            return fix_pit(raw_data['tables'][indx])

        def get_pit_stats():
            return list(map(do_pit, list(range(2,4))))
        return {'bat_stats': get_bat_stats(),
                'pit_stats': get_pit_stats()}
    return pbox_inner(get_game_info(raw_data['game_info']))

def parse_box_main(answer):
    """
    Return lists of batter and pitcher information
    """
    return [pd.concat([answer['bat_stats'][0], answer['bat_stats'][1]],
                        ignore_index=True)[['NAME', 'TEAM', 'DATE', 'POS',
                        'AB', 'R', 'H', 'RBI', 'HR', 'SB']],
        pd.concat([answer['pit_stats'][0], answer['pit_stats'][1]],
                        ignore_index=True)[['NAME', 'TEAM', 'DATE',
                        'WINS', 'SAVES', 'OUTS', 'ER', 'WH', 'SO']]]

def get_answer(url_v):
    """
    Wrapper to add start of http information
    """
    return do_parse_boxscore(get_boxscore(
                    "https://www.cbssports.com" + url_v))

def parse_boxscore(url_v):
    """
    Main entry point
    """
    return parse_box_main(get_answer(url_v))

if __name__ == "__main__":
    print(parse_boxscore("/mlb/gametracker/boxscore/MLB_20230403_NYM@MIL/"))
